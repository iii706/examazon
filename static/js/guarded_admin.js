$(document).ready(function(){
    $(".myspan_select").click(function(){
        let this_obj = $(this);
        let id = $(this).parent().prev().prev().text();
        var curWwwPath = window.document.location.href;
        var pathName=window.document.location.pathname;
        var pos=curWwwPath.indexOf(pathName);
        var localhostPaht=curWwwPath.substring(0,pos);
        let url = localhostPaht+'/product/sellbase_nodisplay/'+id
        $.ajax({
            methon:'GET',
            contentType: "application/json",
            dataType: "json",
            url:url,
            success: function(ret){
               if(ret.msg == 1){
                    this_obj.closest("tr").remove();
                    if ($("tr").length < 10) { //没有多少的时候，刷新本页面
                        window.location.reload();
                    }
               }else{
                    alert("网络错误！")
               }
            }
        });


        //$(this).closest("tr").remove();
    });
//    //$(".field-IMAGE").attr('style', 'width:150px;');
//    $(".field-title").attr('style', 'width:280px;');


});


