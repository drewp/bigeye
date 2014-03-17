pxPerCol = 2
pxPerRow = 4
ledPerPole = 50

class Pole
  constructor: (@elem, @displayedColumns) ->
    @elem.height = pxPerRow * ledPerPole
    @elem.width = @displayedColumns * pxPerCol + 10
    @ctx = @elem.getContext('2d')

    @colors = [] # list of columns of triples

    for col in [0...@displayedColumns]
      c = []
      for row in [0...ledPerPole]
        c.push('#000')
      @colors.push(c)
   
    @currentXCol = 80

  shift: =>
    @colors.splice(0, 1)

  setColumn: (pts, col) =>
    @colors.push(col)

  redraw: =>
    x = 0
    curWidth = 6
    marg = 3
    for col in [0...@colors.length]
      colArray = @colors[col]
      isCurrent = col == @currentXCol
      colWidth = if isCurrent then (marg*2+curWidth) else pxPerCol
      if col >= @currentXCol - 1
        bright = (if (col == @currentXCol) then 1 else .3)
        @drawColumn(colArray, (if isCurrent then x+marg else x), (if isCurrent then curWidth else colWidth), bright)
      x += colWidth 
    @slideRect(0, (@currentXCol) * pxPerCol, -pxPerCol)

  slideRect: (xFrom, width, xTo) =>
    buf = @ctx.getImageData(xFrom, 0, width, @elem.height)
    @ctx.putImageData(buf, xTo, 0)

  drawColumn: (colArray, x, colWidth, brightScale) =>
    scl = 255 * brightScale
    for row in [0...colArray.length]
      [r,g,b] =  colArray[row]
      @ctx.fillStyle = 'rgb(' + Math.round(r*scl) + ',' + Math.round(g*scl) + ',' + Math.round(b*scl) + ')'
      @ctx.fillRect(x, (ledPerPole - row) * pxPerRow, colWidth, pxPerRow - 1)

padHandler = (x,y) -> null

class PadCanvas
  constructor: (@elem, @config) -> # also a cb for picking coord and img color
    console.log("set up in ", @elem, @config)
    title = document.createElement('div')
    title.textContent = @config.title
    @elem.appendChild(title)

    canvas = document.createElement('canvas')
    @elem.appendChild(canvas)
    canvas.width = canvas.height = 64
    ctx = canvas.getContext('2d')
    
    img = new Image()
    img.src = @config.background
    img.onload = =>
      console.log("drawing in bg", img.src)
      ctx.drawImage(img, 0, 0, canvas.width, canvas.height)
      window.img = img
      window.ctx = ctx

    setColorFromMouse = (ev) =>
      px = ctx.getImageData(ev.offsetX, ev.offsetY, 1, 1)
      @config.colorClick?([px.data[0] / 255, px.data[1] / 255, px.data[2] / 255])
      
    canvas.addEventListener('click', setColorFromMouse)
    canvas.addEventListener 'mousemove', (ev) =>
      setColorFromMouse(ev) if ev.which == 1
    padHandler = (x,y) -> setColorFromMouse({offsetX: x/2, offsetY: y/2})

  # click events, midi events
    
ko.bindingHandlers.padCanvas =
  init: (element, valueAccessor, allBindings, viewModel, bindingContext) ->
    new PadCanvas(element, valueAccessor())

class Pole2
  constructor: (@chan) ->
    @inputScale = ko.observable(1)
    @inputGamma = ko.observable(1)
    @primaryColor = ko.observable([1,1,1])
    @brightness = ko.observable(1)

  snowColumn: (frac, frostFraction, primary, snow) =>
    col = []
    ff = 1 - frostFraction
    frac = Math.pow(frac * @inputScale(), @inputGamma())
    primaryRows = Math.round(frac * ff * ledPerPole)
    for x in [0...primaryRows]
      col.push(primary)
    for x in [primaryRows...Math.round(frac * ledPerPole)]
      col.push(snow)
    for x in [0...ledPerPole - col.length + 1]
      col.push([0,0,0])
    col

brighter = (col, scl) ->
  [Math.min(1, col[0] * scl),
   Math.min(1, col[1] * scl),
   Math.min(1, col[2] * scl)]

colorScale = brighter
      
window.addEventListener 'load', ->
  model = window.model =
    pad1: ko.observable([0,0,0])
    master:
      brightness: ko.observable(1)
      heightScale: ko.observable(1)
      frostFraction: ko.observable(.1)
      frostScale: ko.observable(1.4)
    poles: [
      new Pole2('bass'),
      new Pole2('drums'),
      new Pole2('guitar'),
      new Pole2('voice'),
      new Pole2('chan4'),
      new Pole2('chan5'),
    ]
  ko.applyBindings(model)

  for pole in model.poles
      pole.obj = new Pole(document.getElementById('chan-'+pole.chan), 85)

  lastSound = {}
  atOnce = 1
  step = =>
    t = +new Date()
    (p.obj.redraw() for p in model.poles)
    for lp in [0...atOnce]
      for p in model.poles
        p.obj.shift()
        ht = lastSound[p.chan] * model.master.heightScale()
        pc = colorScale(p.primaryColor(), model.master.brightness() * p.brightness())
        col = p.snowColumn(ht, model.master.frostFraction(), pc, brighter(pc, model.master.frostScale()))
        p.obj.setColumn(null, col)
    nextFrame = t + 10
    setTimeout(step, Math.max(0, (nextFrame - (+new Date()))))
  step()

  ws = new WebSocket("ws://localhost:3001/sound")
  ws.onopen = -> console.log("connected")
  ws.onmessage = (ev) ->
    lastSound = JSON.parse(ev.data)

  ws = new WebSocket("ws://localhost:3001/midi")
  ws.onopen = -> console.log("connected")

  lastMidiSeen = {} # data1: data2
  ws.onmessage = (ev) ->
    msg = JSON.parse(ev.data)
    lastMidiSeen[msg.data1] = msg.data2
    
    if msg.data1 == 0 and lastMidiSeen[12] > 30 then model.master.brightness(msg.data2 / 127)
    if msg.data1 == 1 and lastMidiSeen[13] > 30 then model.master.heightScale(msg.data2 / 127)
    if msg.data1 == 2 and lastMidiSeen[14] > 30 then model.master.frostFraction(msg.data2 / 127)
    if msg.data1 == 3 and lastMidiSeen[15] > 30 then model.master.frostScale(msg.data2 / 127)

    if msg.data1 == 23 then model.pad1([msg.data2, model.pad1()[1], model.pad1()[2]])
    if msg.data1 == 24 then model.pad1([model.pad1()[0], msg.data2, model.pad1()[2]])
    if msg.data1 == 25 then model.pad1([model.pad1()[0], model.pad1()[1], msg.data2])
    if model.pad1()[0] > 20
      padHandler(model.pad1()[1], 64 - model.pad1()[2])
