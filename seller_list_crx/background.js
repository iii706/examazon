var start_url = "http://127.0.0.1:8000/product/get_list_url/"
var add_seller_asins_url = "http://127.0.0.1:8000/product/add_seller_asins/"

let listRequest = {
    state: ['token_list'],  // 默认三个令牌 最多可并发发送三次请求
    queue: [],   // 请求队列
    waitqueue: [],  //  等待队列
    // 获取令牌
    getToken: function() {
        return this.state.splice(0, 1)[0];
    },
    // 归还令牌
    backToken: function(token) {
        this.state.push(token);
    },
    // 请求队列
    pushQueue: function(request_obj, type = "first") {
        type == "second" && (this.queue = []); // 每次push新请求的时候  队列清空
        if( this.state.length > 0) {  // 看是否有令牌
            var token = this.getToken();  // 取令牌
            request_obj.token = token;
            this.queue.push(request_obj);
        } else {   // 否则推入等待队列
            this.waitqueue.push(request_obj)
        }
    },
    // 开始执行
    start: function() {
        for(let item of this.queue) {
            if (stop_flag == true){
               console.log("正在采集：",item.url);
               item.request(item.url).then(res => {
                    var jqueryObj = $(res);

                    var filter_ret = jqueryObj.find("#s-all-filters");//判断是否是手机页面
                    var list_div_css_selector = '#search > div.s-desktop-width-max.s-desktop-content.s-opposite-dir.sg-row > div.s-matching-dir.sg-col-16-of-20.sg-col.sg-col-8-of-12.sg-col-12-of-16 > div > span:nth-child(4) > div.s-main-slot.s-result-list.s-search-results.sg-row > div';
                    var review_counts_css_selector = "span.a-size-base.s-underline-text"
                    var price_css_selector = "div.a-row.a-size-base.a-color-base > a > span:nth-child(1) > span.a-offscreen"
                    if(filter_ret.length > 0){
                        list_div_css_selector = "div.s-main-slot.s-result-list.s-search-results.sg-row > div";
                        review_counts_css_selector = "span.a-size-mini.a-color-base.s-light-weight-text";
                        price_css_selector = "a.a-link-normal.s-faceout-link.a-text-normal > span.a-price > span.a-offscreen";
                    }


                    var rets = jqueryObj.find(list_div_css_selector)
                    var asins = [];
                    for(var i = 0; i <= rets.length; i++){
                        var asin = $(rets[i]).attr("data-asin");
                        if(asin != "" && asin != undefined){
                            var review_counts = $(rets[i]).find(review_counts_css_selector).text();
                            var price = $(rets[i]).find(price_css_selector).text();
                            //console.log(asin,review_counts,price);
                            var detail_url_obj = {
                                'url':"https://www.amazon.com/dp/"+asin,
                                'type':'detail_url',
                                'asin':asin,
                                'price':price,
                                'review_counts':review_counts,
                            }
                            //console.log("review_counts结果 ：",parseInt(review_counts) < min_review_counts,parseInt(review_counts),min_review_counts);
                            asins.push(asin);//抓取卖家id不用过滤review数

                        }

                    }

                    res = null;
                    console.log(asins);
                    if(asins.length > 0){

                        let options = {
                                method: 'POST',//post请求
                                headers: {
                                'Accept': 'application/json',
                                'Content-Type': 'application/json'
                                },
                                body: JSON.stringify({//post请求参数
                                    asins: asins.join("|"),
                                    current_url: item.url,
                                    url_id:item.url_id,
                                    current_page:item.current_page
                                })
                        }
                        fetch(add_seller_asins_url,options).then(
                        response => response.json()
                        ).then(
                            res=>console.log(res)
                        );
                    }
                    this.backToken(item.token); // 令牌归还
                    if(this.waitqueue.length > 0){
                        var wait = this.waitqueue.splice(0, 1)[0];
                        this.pushQueue(wait, "second"); // 从等待队列进去的话 就是第二中的push情况了
                        this.start(); // 重新开始执行队列
                    }
                    if(this.state.length == 1){
                        chrome.runtime.reload();
                    }
                });

        }
    }

    }
}


function callback(res){
    msg = res.msg;
    if (msg == 1){
        urls = res.urls;
        console.log(urls)
        for (var i = 0; i < urls.length ; i++  ){
            function f1(url) {
            return new Promise((resolve, reject) => {
                    resolve(fetch(url).then(response => response.text())
                    )
                })
            }
            var request_obj = {
                request:f1,
                url:urls[i].url,
                url_id:res.url_id,
                current_page:urls[i].current_page
            }
            listRequest.pushQueue(request_obj);
        }
        listRequest.start();

    } else if(msg == 2) {
       chrome.runtime.reload();
    } else {
       console.log("没有获取到初始url");
    }
}


fetch(start_url).then(
    response => response.json()
).then(
    res=>callback(res)
)


