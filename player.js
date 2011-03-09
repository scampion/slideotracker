function loadvideo(){
  var mediafile = gup("mediafile");

  var v = document.getElementsByTagName("video")[0];  
  v.addEventListener("loadedmetadata", function() { play();}, true);
  v.src = mediafile ;
  
  current_slide = 0 ;
  var s = document.getElementById("slide");
  s.src = slides[0];
  setInterval("refresh()", 3000);
}


function refresh(){
  var fps = gup("fps");
  var slidedir = gup("slidedir");
  var slide = document.getElementById("slide");
  var v = document.getElementsByTagName("video")[0];  

  current_frame = v.currentTime * fps;
  var i = 0 ;
  for(i=0 ; i < slides.length ; i++){   
    if (current_frame < frames[i] )
      {
	break ;	
      } 
  }
  if ( i != current_slide ){
    current_slide = i ; 	
    document.getElementById("slide").src = slides[i-1];
  }

}
 
// Enable to retrieve parameters 
// for GET http request 
function gup( name )
{
  var regexS = "[\\?&]"+name+"=([^&#]*)";
  var regex = new RegExp( regexS );
  var tmpURL = window.location.href;
  var results = regex.exec( tmpURL );
  if( results == null )
    return "";
  else
    return results[1];
}


function play(){
  var start = gup( 'start' ); 
  var duration = gup( 'duration' ); 
  var v = document.getElementsByTagName("video")[0];  
  v.currentTime = start ;
  v.play();
  if (duration ) {
    setTimeout("pause();",duration*1000);
  }
}

