function httpget(theUrl)  {
    var xmlHttp = null;
    xmlHttp = new XMLHttpRequest();
    xmlHttp.open( "GET", theUrl, false );
    xmlHttp.send( null );
    return xmlHttp.responseText;
  }

function jsDrawTab(obj){
    document.getElementById("tabcontent").innerHTML = obj;
}

function jsDrawQStatus(obj){
    document.getElementById("queue_status").innerHTML = obj;
    console.log(obj);
}

function ajgetQStatus(){
    jsDrawQStatus(httpget('status'));
    }

var QStatus = function() {
    ajgetQStatus();
    TableUpdater = setInterval(ajgetQStatus, 100000);
};

$(function() {
    QStatus();
});
