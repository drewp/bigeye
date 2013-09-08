
function Ctrl($scope, $http) {


    function onMessage(d) {
        $scope.$broadcast("socketMessage", d)
    }

    $scope.socket = reconnectingWebSocket("ws://localhost:9991/live", onMessage);

}
 
angular.module('bigeye', [])
  .directive('waveform', [function () {
    return {
      restrict: 'E',
      replace: true,
      transclude: true,
        scope: {
            name: "@",
            },
      template: '<div class="waveform">' +
                  '{{name}} {{points}} <canvas></canvas>' +
                '</div>',

      link: function(scope, element, attrs) {
          var canvas = element[0].getElementsByTagName("canvas")[0];
          var ctx = canvas.getContext("2d");

          function repaint(pts) {
              ctx.clearRect (0, 0, canvas.width, canvas.height);
              if (pts.length == 0) {
                  return;
              }
              ctx.beginPath();
              ctx.moveTo(0, 0);
              for (var i = 0; i < pts.length; i++) {
                  var x = i / (pts.length - 1) * canvas.width;
                  ctx.lineTo(x, pts[i]);
              }
              ctx.stroke();
          }
          
          scope.points = [];
          var socket = scope.$parent.socket;
          scope.$on('socketMessage', function (event, d) {
              scope.$apply(function (scope) {
                  if (d.points) {
                      scope.points = d.points;
                      repaint(d.points);
                  }
              });
          });
          function update() {
              if (socket.readyState == WebSocket.OPEN) {
                  socket.send("getWaveform");
              }
              setTimeout(update, 1000);
          }
          update();
      },
    }
  }])
  .directive('param', ['$http', function($http) {
    return {
      restrict: 'E',
      replace: true,
      transclude: true,
        scope: {
            name: "@",
            },
      template: '<div class="param">' +
                  '{{name}}: <input type="text" ng-model="value"> <input type="range" ng-model="value">' +
                '</div>',

      link: function(scope, element, attrs) {
           $http.get("params").success(function (params) {
               scope.value = params[scope.name];
               
           });
          scope.$watch('value', function (newValue, oldValue) {
              if (newValue === oldValue) {
                  return;
              }
              console.log("w", newValue, oldValue);
              $http.put("params/" + scope.name, newValue);
          });
      }
    }
  }]);
