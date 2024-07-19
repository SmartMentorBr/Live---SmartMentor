//CONFIGURAÇOES BÁSICAS

Chart.defaults.global.multiTooltipTemplate = "<%=datasetLabel%> : <%=value%>";
Chart.defaults.global.responsive =  true;
Chart.defaults.global.animation = false;
Chart.defaults.Line.bezierCurve = false;
Chart.defaults.Line.scaleLineColor =  "rgba(0,0,0,0.3)";

//DEFINIÇÕES GRADE
Chart.defaults.Line.scaleGridLineColor  =  "rgba(0,0,0,0.6)";
Chart.defaults.Line.scaleGridLineWidth  =  0.5;
Chart.defaults.Line.datasetStrokeWidth  =  2.5;
Chart.defaults.Line.scaleShowVerticalLines =  false;
Chart.defaults.Line.scaleShowHorizontalLines =  true;
Chart.defaults.Line.scaleFontSize =  14;
Chart.defaults.Line.scaleFontStyle = 'bolder';

//PONTOS
Chart.defaults.Line.pointDotRadius  =  4;


$.ajax({
    url: 'data_charts',
    success: function(data) {
        
        var canvas = document.getElementsByTagName('canvas'),
            ctx = {},
            graficos = {};

        //ARMAZENAR OS CONTEXTOS DO CANVAS EM OBJETOS
        for(i = 0;i < canvas.length;i++){
            ctx[i] = document.getElementById('chart'+i).getContext('2d');
        }

        //PLOTANDO OS GRÁFICOS NA TELA
        for(i=0;i<data.length;i++){
            graficos[i] = new Chart(ctx[i]).Line(data[i]);
        }
    },
    error: function(data){
        console.log(data);
    }
});


function set_dimensions_canvas(){

    chart_full = document.getElementsByClassName('chart-full')[0];
    chart_half = document.getElementsByClassName('chart-half')[0];

    canvas = document.querySelectorAll('canvas');

    for(i = 0;i <= canvas.length-1;i++){

        pai = canvas[i].parentNode.className;
        
        if (pai == 'chart-full') {
            canvas[i].width = chart_full.offsetWidth;
            canvas[i].height = chart_full.offsetHeight;

        }else if (pai == 'chart-half'){
            canvas[i].width = chart_half.offsetWidth;
            canvas[i].height = chart_half.offsetHeight;
        }
    }
}
