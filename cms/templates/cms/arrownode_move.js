createsvg();

function createsvg () {
  var svg = d3.select("#example").append("svg")
      .attr({
        width: 640,
        height: 480,
      });
  var r1 = 30;
  var r2 = 20;
  var ref1 = 8;
  var c1 = [150, 140, r1,"id1"];
  var c2 = [250, 170, r2, "id2"];
  var carray = [c1, c2];
  // defs/markerという構造で、svgの下に矢印を定義します。
  var marker = svg.append("defs").append("marker")
      .attr({
        'id': "arrowhead",
        'refX': ref1,
        'refY': 2,
        'markerWidth': 4,
        'markerHeight': 4,
        'orient': "auto"
      });
  // 矢印の形をpathで定義します。
  marker.append("path")
      .attr({
        d: "M 0,0 V 4 L4,2 Z",
        fill: "steelblue"
      });


  // 10種類の色を返す関数を使う
  var color = d3.scale.category10();

  var g = svg.selectAll('g')
    .data(carray).enter().append('g')
    .attr({
    // 座標設定を動的に行う
      id: function(d) { return d[3]; },
      transform: function(d) {
    return "translate(" + d[0] + "," + d[1] + ")";
      },
    });

  g.append('circle')
    .attr({
      'r': function(d) { return d[2]; },
      'fill': function(d,i) { return color(i); },
    });

  g.append('text')
    .attr({
      'text-anchor': "middle",
      'dy': ".35em",
      'fill': 'white',
    })
    .text(function(d,i) { return i+1; });

  var line = d3.svg.line()
      .interpolate('basis')
      .x(function(d) {return d[0];})
      .y(function(d) {return d[1];});

  var path = svg.append('path')
      .attr({
        'd': line(carray),
        'id': 'nodepath',
        'stroke': 'lightgreen',
        'stroke-width': 5,
        'fill': 'none',
        // pathのアトリビュートとして、上で定義した矢印を指定します
        'marker-end':"url(#arrowhead)",
      });
  var t = path.node().getTotalLength();
  var tdiff = t - (r1+r2+ref1);
  path.attr({
    'stroke-dasharray': "0 " + r1 + " " + tdiff + " " + r2,
    'stroke-dashoffset': 0,
  });
  var t2 = t*2;
  // pathとしての円を描くのに、d3.svg.lineで点を並べてつなぐ方法は遅いので、svgのpath:aコマンドを使用
  // 参考：http://stackoverflow.com/questions/5737975/circle-drawing-with-svgs-arc-path
  // パスは表示しないので、strokeを定義しない。
  var str = "M0,0 M-" + t + ",0 a" + t + ","+ t + " 0 1,1 " + t2 + ",0 a" + t + "," + t + " 0 1,1 -" + t2 + ",0";
  var path3 = svg.append("path")
    .attr({
      'd': str,
      'fill': "none",
      // 下のコメントを外すと、pathが表示できる
      'stroke': "lightgreen",
      'transform': "translate("+c1[0]+","+c1[1]+")",
    });

  // 動かしたい円を指定する（あらかじめidを設定している） 
  function movecircle(){
    svg.selectAll('#id2')
    .transition()
    // ５秒かけて一周させる
    .duration(7000)
    // easeを指定すると、transitionで変化させるパラメータを[0->1]にすることができる。
    .ease("linear")
    .attrTween(
    // 座標設定を動的に行う
      'transform', function(d,i) {
        // easeで設定したパラメータがtとなって渡ってくる
        return function(t) {
          // path(ここでは円)の座標を取得する
          var p = path3.node().getPointAtLength(path3.node().getTotalLength()*t);
          c2[0] = c1[0]+p.x;
          c2[1] = c1[1]+p.y;
          // 矢印線の座標も変更する。こちらもidを設定している
          svg.selectAll('#nodepath').attr('d', line(carray));
          return "translate(" + c2[0] + "," + c2[1] + ")";
        };
      }
    )
    // 次の行のコメントするとループしなくなる
    .each("end", function() {movecircle()});
  };
  movecircle();
};