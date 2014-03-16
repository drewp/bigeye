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
    

snowColumn = (frac, primary, snow) ->
  col = []

  for x in [0...Math.round(frac * .7 * ledPerPole)]
    col.push(primary)
  for x in [Math.round(frac * .7 * ledPerPole)...Math.round(frac * ledPerPole)]
    col.push(snow)
  for x in [0...ledPerPole - col.length + 1]
    col.push([0,0,0])
  col
    
window.addEventListener 'load', ->
  poles = (new Pole(document.getElementById('pole'+i), 100) for i in [0...6])
  i = 0
  atOnce = 1
  step = =>
    t = +new Date()
    (p.redraw() for p in poles)
    for lp in [0...atOnce]
      (p.shift() for p in poles)
    i++
    if true
      nextFrame = t + 20
      for lp in [0...atOnce]
        tFrac = t + 15 * lp / atOnce
        for n in [0...6]
          p = poles[n]
          ht = (
            .3 +
            .2 * Math.sin(tFrac  / 40) +
            .1 * Math.sin((tFrac - 200) / 20) 
          )
          ht = ht * Math.max(0, .3 + .7 * Math.max(0, Math.sin((tFrac + n * 500) / 900)))

          col = snowColumn(ht, [
                  Math.abs(Math.sin(n)),
                  Math.abs(Math.cos(n)),
                  0], [1, 1, 0])
          p.setColumn(null, col)
      setTimeout(step, Math.max(0, (nextFrame - (+new Date()))))
  step()

  ws = new WebSocket("ws://localhost:3001/sound")
  ws.onopen = -> console.log("connected")
  ws.onmessage = (ev) -> console.log("got", window.ev = JSON.parse(ev.data))
  window.ws = ws
