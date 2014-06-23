include </home/drewp/Downloads/openscad/libraries/MCAD/units.scad>;
include </home/drewp/Downloads/openscad/libraries/MCAD/utilities.scad>;

foot = 12 * inch;
// https://grabcad.com/library/arduino-nano--1

module tube(od, id, height, tz) {
    translate([0,0,tz])
    difference() {
        cylinder(r = od, h = height);
        translate([0,0,-.5])
          cylinder(r = id, h = height + 1);
    }
}

module nano() {
    cube(size=[1.7*inch, .73*inch, 2]);
    pin = 8;
    for (x = [0 : .1*inch : 1.7*inch]) {
        translate([x,0,-pin]) cylinder(r=.5, h=pin, $fn=20);
        translate([x,.73*inch,-pin]) cylinder(r=.5, h=pin, $fn=20);
    }
}
module socket() {
    scale(3)
    difference() {
        union() {
            scale([1,1,.2]) sphere(3, $fn=20);
            translate([0,0,-6]) cylinder(r=3, h=6, $fn=20);
        }
        translate([0,0,-4]) cylinder(r=1.9, h=5, $fn=20);
    }
}

module positionedSocket() {
    translate([-20, -110, 25])
    rotate(60, [1,0,0])
    color([.6,.6,.7,.8])
    socket();
}

module cubeFromTo(from=[0,0,0], to=[1,1,1]) {
    translate(from)
    cube(to - from);
}

module tunnel() {
    cubeFromTo([-20,-40, -1], [20, 0, 101]);
    cubeFromTo([-20,-100,-1], [20,0,11]);
    cubeFromTo([-15,-90,-1], [15,-60,60]);
}

tubeOd = 1.75*inch;
tubeId = 1.5*inch;
module stand(tubeTz=10, tubeGap=1) {
    
    difference() {
        translate([0,0,0]) rotate(360/8*.5, [0,0,1]) 
        difference() {
            cylinder(h=100, r1=130, r2=70, $fn=8);
            // see inside cylinder:
            //scale(.9) translate([0,0,-.1]) cylinder(h=100, r1=130, r2=70, $fn=8);
        }
        
        tube(tubeOd + tubeGap, tubeId - tubeGap, 6*foot, tubeTz);

        // arduino cavity
        translate([-20,-100,30]) cube([40,50,50]);

        hull() { positionedSocket(); }
        tunnel();
    }
    % positionedSocket();
    
    % translate([10,-100,50]) rotate(90, [0,0,1]) nano();
}

module topBracket(tall=20, thick=5, id=tubeOd+2, tongue=80, screwHole=4, screwHead=8) {
    difference() {
        cylinder(h=tall, r=id + thick);
        translate([0,0,-1])
        cylinder(h=101, r=id);
    }
    difference() {
        cubeFromTo([id, 0, 0], [id + thick, tongue, tall]);
        translate([tubeOd - 1, tongue-tall/2, tall/2]) rotate(90, [0,1,0]) {
            cylinder(h=100, r=screwHole);
            cylinder(h=1 + thick/2, r=screwHead);
        }
    }
}

tubeTz = 10;
% tube(tubeOd, tubeId, 6*foot, tubeTz, $fn=200);
stand(tubeTz=tubeTz, $fn=100);
translate([0,0, 1 * foot]) topBracket($fn=100);
