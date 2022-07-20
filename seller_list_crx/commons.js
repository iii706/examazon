//日志输出
//function add_log_text(text){
//
//    let new_time = formatDate(new Date().getTime());
//
//    let oldvalue = $("#loggertextarea")[0].value;
//    if (oldvalue != undefined ){
//        var oldvalue_split = oldvalue.split("\n");
//        if(oldvalue != "" && oldvalue_split.length > 10){
//            var new_value = oldvalue_split.splice(1,oldvalue_split.length).join('\n')+'\n'+ new_time + " " +text;
//            $("#loggertextarea")[0].value = new_value;
//        }else{
//            if (oldvalue == "") {
//                $("#loggertextarea")[0].value = new_time + " " +text;
//            } else{
//                $("#loggertextarea")[0].value = oldvalue+'\n'+ new_time + " " + text;
//            }
//
//        }
//    }
//
//}
//function post_to_locale(data){
//        $.ajax({
//            async : true,
//            url : "http://127.0.0.1:8000/product/post",
//            type : "GET",
//            dataType : "jsonp", // 返回的数据类型，设置为JSONP方式
//            jsonp : 'callback', //指定一个查询参数名称来覆盖默认的 jsonp 回调参数名 callback
//            jsonpCallback: 'handleResponse', //设置回调函数名
//            data : data,
//            success: function(response, status, xhr){
//                xhr = null
//            },
//            complete: function (XHR, TS) { XHR = null }
//            });
//}

//product_url:http://127.0.0.1:8000/product/product_post
//seller_url:http://127.0.0.1:8000/product/seller_post

function post_to_locale(data){
     return $.ajax({
             methon : "get",
             async : true,
             dataType : "json",
             data : data,
             url : "http://127.0.0.1:8000/product/post/", //跨域请求的URL
             success : function(response, status, xhr){
                 xhr = null
             },
             complete: function (XHR, TS) { XHR = null }
    });
}



//时间格式化 formatDate(new Date().getTime())
function formatDate(time){
    var date = new Date(time);

    var year = date.getFullYear(),
        month = date.getMonth()+1,//月份是从0开始的
        day = date.getDate(),
        hour = date.getHours(),
        min = date.getMinutes(),
        sec = date.getSeconds();
    var newTime = year + '-' +
                (month < 10? '0' + month : month) + '-' +
                (day < 10? '0' + day : day) + ' ' +
                (hour < 10? '0' + hour : hour) + ':' +
                (min < 10? '0' + min : min) + ':' +
                (sec < 10? '0' + sec : sec);

    return newTime;         
}
