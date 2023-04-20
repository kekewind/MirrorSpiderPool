$(document).ready(function(){
  $(".zhan").click(function(){
  $(".yin").toggle();
  });
});
function formatDateTime(inputTime) {    
        var date = new Date(inputTime);  
        var y = date.getFullYear();    
        var m = date.getMonth() + 1;    
        m = m < 10 ? ('0' + m) : m;    
        var d = date.getDate();    
        d = d < 10 ? ('0' + d) : d;    
        var h = date.getHours();  
        h = h < 10 ? ('0' + h) : h;  
        var minute = date.getMinutes();  
        var second = date.getSeconds();  
        minute = minute < 10 ? ('0' + minute) : minute;    
        second = second < 10 ? ('0' + second) : second;   
        return  y + '-'+ m + '-' + d+' '+h+':'+minute;    
}; 	
$(function(){
	var cid = document.getElementById('jsclassid').getAttribute('cid');
	var winH = $(window).height(); //页面可视区域高度
	var i = 1;
	var loading = false;
	var domain = document.domain;
	$(window).scroll(function () {
	    var pageH = $(document.body).height();
		var scrollT = $(window).scrollTop(); //滚动条top
		var aa = (pageH-winH-scrollT)/winH;
		if(aa<0.02){
		if(!loading){
			loading = true;
			$.getJSON('/znlistmore?channel_id='+cid,{page:i},function(json){
				if(json){
					var str = "";
					var listi= 0;
					var radio="";
					var video="";
					$.each(json,function(index,array){
					if(array['list_kind']==0){
						var str = '      <div class="box"  style="position: relative;">';
						var str = str + '<div class="box-text-text">';
						var str = str + '<div class="box-text-title" style="height:60%"><a href="/zncontent/' + array['id'] + '.html" target="_blank">' + array['title'] + '</a></div>';
						var str = str + '<div class="box-text-time" style="margin-top:2px"><span>' + array['date_create'] + '</span><span style="float:right"><img src="https://news.yangtse.com/images/play.png" width="14px"/> </span></div>';
						var str = str + '</div>';
						var str = str + '<div class="clear"></div>';
						var str = str + '</div>';
					}else{
						var str = '      <div class="box"  style="position: relative;">';
						var str = str + '<div class="box-img"><a href="/zncontent/' + array['id'] + '.html" target="_blank"><img src="' + array['img_43'] + '" width="200" height="135" /></a></div>';
						var str = str + '<div class="box-text">';
						var str = str + '<div class="box-text-title" style="height:60%"><a href="/zncontent/' + array['id'] + '.html" target="_blank">' + array['title'] + '</a></div>';
						var str = str + '<div class="box-text-time" style="margin-top:2px"><span>' + array['date_create'] + '</span><span style="float:right"><img src="https://news.yangtse.com/images/play.png" width="14px"/> </span></div>';
						var str = str + '</div>';
						var str = str + '<div class="clear"></div>';
						var str = str + '</div>';
					}	
						$("#morepage").append(str);
					});
					i++;
					loading = false;
				}else{
					$(".nodata").show().html("别滚动了，已经到底了。。。");
					return false;
				}
			});
		}
		}
	});
});	 