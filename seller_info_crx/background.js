
var get_seller_asins = "http://127.0.0.1:8000/product/get_seller_asins/"
var add_seller_info_url = "http://127.0.0.1:8000/product/add_seller_info/"
var add_seller_re_asins_url = "http://127.0.0.1:8000/product/add_seller_re_asins/"


function chrome_reload(time){
    function sleep (time) {
        return new Promise((resolve) => setTimeout(resolve, time));
    }

    // 用法
    sleep(time).then(() => {
        chrome.runtime.reload()
    })
}

let detailRequest = {
    state: ['token1','token2','token3','token4'],  // 默认三个令牌 最多可并发发送三次请求
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
               product_url = 'https://www.amazon.com/dp/'+item.asin
               item.request(product_url).then(res => {


                var jqueryObj = $(res);

                var title = jqueryObj.find("h4").text()


                if(title == "Enter the characters you see belowType the characters you see in this image:"){
                    console.log(title,'status,200 web block!!')
                    chrome_reload(50000)
                }
                var default_Paser = product_Paser
                var mobile_flag = false
                var title_ret = jqueryObj.find("#productTitle")//判断是否是手机页面

                if(title_ret.length == 0 ){
                    default_Paser = mobile_product_Paser;
                    mobile_flag = true
                }


                var data = {
                    'seller_id':"",
                    'asin':item.asin
                };
                var seller_url = product_extract(jqueryObj,default_Paser.seller_url,"seller_url");
                if(seller_url != "" && seller_url != undefined) {
                    if (seller_url.indexOf("seller=") != -1){
                        data['seller_id'] = seller_url.split("seller=")[1].split("&")[0]
                    }
                }
                //console.log("data数据是：",data);
                if(item.asin != undefined && data.seller_id != ""){
                    data['ret'] = 1;
                } else {
                    data['ret'] = 0;
                }

                let options = {
                                method: 'POST',//post请求
                                headers: {
                                'Accept': 'application/json',
                                'Content-Type': 'application/json'
                                },
                                body: JSON.stringify(data)
                        }
                    console.log(data);
                    fetch(add_seller_info_url,options).then(
                    response => response.json()
                    ).then(
                        res=>console.log(res)
                    );

                    //抓取关联的asins
                    var a_links = jqueryObj.find("a")
                    const asins = new Set();
                    for (var i =0; i < a_links.length; i++){
                        var href = $(a_links[i]).attr("href")
                        var myRe = /\/.*?\/dp\/([A-Z0-9]{10})\/ref=.*?/gm;
                        if (href != undefined){
                            var re_ret = href.match(myRe)
                            if(re_ret){
                                asins.add(RegExp.$1)
                            }
                        }
                    }
                    for (var i =0; i < a_links.length; i++){
                        var href = $(a_links[i]).attr("href")
                        var myRe = /pd_rd_i%3D([A-Z0-9]{10})%26pd_rd_w/gm;
                        if (href != undefined){
                            var re_ret = href.match(myRe)
                            if(re_ret){
                                asins.add(RegExp.$1)
                            }
                        }
                    }
                    if(asins.size > 0){
                        var asin_str = Array.from(asins).join("|")
                        console.log("关联的asins:",asin_str)
                        let options = {
                                method: 'POST',//post请求
                                headers: {
                                'Accept': 'application/json',
                                'Content-Type': 'application/json'
                                },
                                body: JSON.stringify({//post请求参数
                                    asins: asin_str
                                })
                        }
                        fetch(add_seller_re_asins_url,options).then(
                        response => response.json()
                        ).then(
                            res=>console.log(res)
                        );
                    }





                res = null;
                this.backToken(item.token); // 令牌归还

                if(this.waitqueue.length > 0) {
                    var wait = this.waitqueue.splice(0, 1)[0];
                    this.pushQueue(wait, "second"); // 从等待队列进去的话 就是第二中的push情况了
                    this.start(); // 重新开始执行队列
                }

                if (this.state.length == 4){
                    chrome_reload(3000)
                }


                }).catch(e => {
                    if (e.status === 404) {
                        var data = {
                            'ret':1,
                            'asin':item.asin
                        }
                        console.log("异常404了"); //找不到这个asin，提交删除的请求
                        let options = {
                                method: 'POST',//post请求
                                headers: {
                                'Accept': 'application/json',
                                'Content-Type': 'application/json'
                                },
                                body: JSON.stringify(data)
                                }
                        fetch(add_seller_info_url,options).then(
                        response => response.json()
                        ).then(
                            res=>console.log(res)
                        );
                        }
                });
            }
        }
    },

}

function callback(res){
    msg = res.msg;
    if (msg == 1){
        asins = res.asins;
        //console.log(asins)
        for (var i = 0; i < asins.length ; i++  ){
            function f1(url) {
            return new Promise((resolve, reject) => {
                    resolve(fetch(url).then(response => {
                            if(response.ok){
                                return response.text(); //200代码
                            }else{
                               return Promise.reject({ //异常抛出意外
                                status: response.status,
                                statusText: response.statusText
                                })
                            }
                        })
                    )
                })
            }
            var request_obj = {
                request:f1,
                asin:asins[i],
                //asin:'B09ZV1GYDJ',
            }
            detailRequest.pushQueue(request_obj);
        }
        detailRequest.start();

    } else {
       console.log("没有获取到需要抓取的产品链接");
    }
}

fetch(get_seller_asins).then(
    response => response.json()
    ).then(
        res=>callback(res)
    );

function sleep (time) {
  return new Promise((resolve) => setInterval(resolve, time));
}

// 用法
sleep(50000).then(() => {
   chrome.runtime.reload()
})




