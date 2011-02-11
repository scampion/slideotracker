function loadvideo(){
  var slidedir = gup("slidedir");
  var mediafile = gup("mediafile");

  var v = document.getElementsByTagName("video")[0];  
  v.addEventListener("loadedmetadata", function() { play();}, true);
  v.src = mediafile ;

  current_slide = 0 

  var slide = document.getElementById("slide");
  var slidepath = slidedir+'/slide-'+current_slide+'.jpg'  ;

  slide.innerHTML = "<img height='328' src='"+slidepath+"' />" ;
  setInterval("refresh()", 1000);
}


function refresh(){
  var fps = gup("fps");
  var slidedir = gup("slidedir");
  var slide = document.getElementById("slide");
  var v = document.getElementsByTagName("video")[0];  

  current_frame = v.currentTime*fps ;
  var i = 0 ;
  for(i=0 ; i<slides.length ; i++){   
    if (current_frame < frames[i] )
      {
	break ;	
      } 
  }

  if ( i != current_slide ){
    current_slide = i ; 	
    var slidepath = slidedir+'/slide-'+slides[i]+'.jpg'  ;
    slide.innerHTML = "<img height='328' src='"+slidepath+"' />" ;
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

