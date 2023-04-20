var tt = nn =0, count;
$(document).ready(function(){ 
count=$("#fbanner_list a").length;
$("#fbanner_list a:not(:first-child)").hide();
$("#fbanner_info").html($("#fbanner_list a:first-child").find("img").attr('alt'));
$("#fbanner_info").click(function(){window.open($("#fbanner_list a:first-child").attr('href'), "_blank")});
$("#fbanner li").click(function() {
var ii = $(this).text() -1;//获取Li元素内的值，即1，2，3，4
nn = ii;
if (ii >= count) return;
$("#fbanner_info").html($("#fbanner_list a").eq(ii).find("img").attr('alt'));
$("#fbanner_info").unbind().click(function(){window.open($("#fbanner_list a").eq(ii).attr('href'), "_blank")})
$("#fbanner_list a").filter(":visible").fadeOut(500).parent().children().eq(ii).fadeIn(1000);
document.getElementById("fbanner").style.background="";
$(this).toggleClass("on");
$(this).siblings().removeAttr("class");
});
tt = setInterval("showAuto()", 4000);
$("#fbanner").hover(function(){clearInterval(tt)}, function(){tt = setInterval("showAuto()", 4000);});
})
function showAuto()
{
nn = nn >=(count -1) ?0 : ++nn;
$("#fbanner li").eq(nn).trigger('click');
}

    window.onload= function() {
        var box  = document.getElementById("all");  //   获得大盒子
        var ul = box.children[0].children[0];  // 获取ul
        var ulLis = ul.children;  //  ul 里面的所有  li
        // 复习：  cloneNode()     克隆节点       追加a.appendChild(b)  把b 放到a 的最后面
        //1.  ulLis[0].cloneNode(true)  克隆  节点
        ul.appendChild(ulLis[0].cloneNode(true));   // ul 是 a   ulLis[0].cloneNode(true) 是b

        //2. 插入 ol 里面的li
        var ol = box.children[1];  // 获得ol
        // 因为 我们要创建很多个 ol 里面的li 所以需要用到for 循环哦
        for(var i=0;i<ulLis.length-1;i++) {   // ul 里面的li  长度 要减去 1  因为我们克隆一个
            // 创建节点 li
            var li = document.createElement("li");
            li.innerHTML = i + 1;   //  存在加1 的关系
            // a.appendChild(b);
            ol.appendChild(li);
        }
        var olLis = ol.children;  // 找到 ol 里面的li
        olLis[0].className = 'current';
        // 3. 动画部分  遍历小li ol
        for(var i=0;i<olLis.length;i++) {
            olLis[i].index = i;  // 赋予索引号
            olLis[i].onmouseover = function() {
                // 清除所有人
                for(var j=0;j<olLis.length;j++) {
                    olLis[j].className = "";
                }
                this.className = 'current';
                animate(ul,-this.index*ulLis[0].offsetWidth);
                key = square = this.index; // 鼠标经过 key square 要等于 当前的索引号
            }
        }
       // 4. 定时器部分  难点
        var timer = null;  // 定时器
        var key = 0; // 用来控制图片的播放的
        var square = 0;  // 用来控制小方块的
        timer = setInterval(autoplay,3000);   // 每隔3s 调用一次 autoplay
        function autoplay() {
            key++;   // key == 1  先 ++
            console.log(key); //  不能超过5
            if(key > ulLis.length - 1)
            {
               // alert('停下');
                ul.style.left = 0;
                key = 1;  // 因为第6张就是第一张，我们已经播放完毕了， 下一次播放第2张
                // 第2张的索引号是1
            }
            animate(ul,-key*ulLis[0].offsetWidth);
            // 小方块的做法
            square++;  // 小方块自加1
            square = square>olLis.length-1 ? 0 : square;
            /// 清除所有人
            for(var i=0;i<olLis.length;i++) {
                olLis[i].className = "";
            }
            olLis[square].className = "current";   // 留下当前自己的

        }


        // 鼠标经过和停止定时器
        box.onmouseover = function() {
            clearInterval(timer);
        }

        box.onmouseout = function() {
            timer = setInterval(autoplay,3000);  // 一定这么开
        }



        //  基本封装
        function animate(obj,target) {
            clearInterval(obj.timer);  // 要开启定时器，先清除以前定时器
            // 有2个参数 第一个 对象谁做动画  第二 距离 到哪里
            // 如果 offsetLeft 大于了  target 目标位置就应该反方向
            var speed = obj.offsetLeft < target ? 15 : -15;
            obj.timer = setInterval(function() {
                var result = target - obj.offsetLeft;  //  他们的值 等于 0 说明完全相等
                // 动画的原理
                obj.style.left = obj.offsetLeft + speed  + "px";
                if(Math.abs(result) <= 15) {
                    obj.style.left = target + "px";   //抖动问题
                    clearInterval(obj.timer);
                }
            },10);
        }

    }

        function timer(opj){
            $(opj).find('ul').animate({
                marginTop : "-20px"  
                },500,function(){  
                $(this).css({marginTop : "0px"}).find("li:first").appendTo(this);  
            })  
        }
        $(function(){ 
            var num = $('.notice_active').find('li').length;
            if(num > 1){
               var time=setInterval('timer(".notice_active")',3500);
                $('.gg_more a').mousemove(function(){
                    clearInterval(time);
                }).mouseout(function(){
                    time = setInterval('timer(".notice_active")',3500);
                }); 
            }
            
            $(".news_ck").click(function(){
                location.href = $(".notice_active .notice_active_ch").children(":input").val();
            })
        });
