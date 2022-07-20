let detail_start_flag = true;
let stop_flag = true;
let page_start = 1;
let page_end = 200;
let min_review_counts = 300;
let max_rank = 60000;
let add_date_year_filter = ['2021','2022']  //合适年份
let list_url = "";
let list_urls = [];

let seller_Paser = {
	'brand_name':['#sellerName-rd'],
	'days_30_ratings':['#feedback-summary-table > tbody > tr:nth-child(5) > td:nth-child(2) > span'],
	'days_90_ratings':['#feedback-summary-table > tbody > tr:nth-child(5) > td:nth-child(3) > span'],
	'year_ratings':['#feedback-summary-table > tbody > tr:nth-child(5) > td:nth-child(4) > span'],
	'life_ratings':['#feedback-summary-table > tbody > tr:nth-child(5) > td:nth-child(5) > span'],
	'business_name':['#page-section-detail-seller-info > div > div > div > div:nth-child(2) > span:nth-child(2)'],
	'business_addr':['div.a-row.a-spacing-none.indent-left']
    }

let product_Paser = {
	'title':['#productTitle'],
	'image':['#landingImage'],
	'price':['#corePrice_feature_div > div > span > span.a-offscreen',
			'#comparison_price_row > td.comparison_baseitem_column > span > span.a-offscreen'
			],
	'desc':["#detailBulletsWrapper_feature_div","#productDetails-placement-auto_feature_div","#prodDetails"],
	'seller_url':['#sellerProfileTriggerId']
}



//解析产品详细信息方法
function paserDesc(str){
    var myRe = /<script[\s\S]*<\/script>/gm;
    str = str.replace(myRe,"");
    var myRe2 = /<style[\s\S]*<\/style>/gm;
    str = str.replace(myRe2,"");
    var rets = $(str).find("span.a-list-item");
    //console.log("长度：",rets.length);
    if(rets.length == 0){
        rets = $(str).find("tr");
        //console.log("长度1：",rets.length);
    }

    var ret_datas = [];
    for (var i = 0; i<= rets.length; i++){

        var new_texts = $(rets[i]).text();
        new_texts = new_texts.replace(/\n/gm,"");
        new_texts = new_texts.replace("‎ ","")
        new_texts = new_texts.replace(" ‏","")
        new_texts = new_texts.replace(":","");
        new_texts = new_texts.replace(/\sx\s/,"x");
        new_texts = new_texts.replace(/\sx/,"x");
        new_texts = new_texts.replace(/x\s/,"x");
        new_texts = new_texts.replace("LxWxH","");
        new_texts = new_texts.replace("Product Dimensions","Package Dimensions");
        new_texts = $.trim(new_texts);
        new_texts = new_texts.replace(/\s{1,}/gm," ");
        new_texts = new_texts.replace(/\s{1,}/gm," ");

        if( new_texts!= ""){
                //console.log("文本内容：",new_texts);
                //console.log(new_texts.indexOf("Product Dimensions"));
            if (new_texts.indexOf("Weight") != -1 || new_texts.indexOf("Package Dimensions") != -1 || new_texts.indexOf("ASIN") != -1 || new_texts.indexOf("Reviews") != -1 || new_texts.indexOf("Best Sellers Rank") != -1 || new_texts.indexOf("Date First Available") != -1){
                new_texts = new_texts.split(" (See Top 100")[0];

                if(new_texts.indexOf("Dimensions") != -1){
                    if(new_texts.indexOf("inches") != -1){
                    //console.log("文本内容2131：",new_texts);
                    ret_datas.push(new_texts);
                    continue;
                    } else {
                    continue;
                    }
                }

                if(new_texts.indexOf("ratings") != -1){
                    new_texts = new_texts.split("ratings")[0] + "ratings"
                }

                //console.log("文本内容：",new_texts);
                if(new_texts.indexOf("Best Sellers Rank") != -1){
                    var rank = $.trim(new_texts.replace("Best Sellers Rank","").split(' in ')[0].replace('#', '').replace(',', ''))
                    rank = parseInt(rank)
                    //console.log("rank是：",rank)
                    if(rank >= max_rank){ //设置最大的排名：
                        return "";
                    }
                }
                if(new_texts.indexOf("Date First Available") != -1){
                    var add_date_year = $.trim(new_texts.replace("Date First Available",'').split(",")[1])
                    //console.log("上架年份是：",add_date_year)
                    if(add_date_year_filter.indexOf(add_date_year) == -1){ //设置是否是21年，22年的产品：
                        return "";
                    }
                }


                ret_datas.push(new_texts);
            }

        }



    }
    if(ret_datas.join("|").indexOf("Date First Available") == -1){
        return ""; //没有上架时间不保存
    }

    return ret_datas.join("|");

}

//解析产品页面
function product_extract(jqueryObj,selector,key){
	for (var i = 0; i <= selector.length; i++){
		if (typeof(selector[i]) != "undefined"){
			var ret = jqueryObj.find(selector[i]);
			if (key == "price"){
				if(ret.length == 0){
					return 0.0;
				}
			}
			if (key == "desc"){
				if (ret.text() != ""){
                    var datas = paserDesc(ret.html())
                    //console.log(datas,ret.html());
					return datas;
				}
			}

			if(key == "seller_url"){

			    var seller_url = ret.attr("href");
			   if (seller_url != ""){
			    return seller_url;
			   }
			}

			if (typeof(ret) != "undefined"){
				if (key == "image"){
						return ret.attr("src");
					}
				if(ret.text() != ""){
					return $.trim(ret.text());
				}

			} else{
				return "#NA";
		}
		}
	}
}


function seller_extract(jqueryObj,selector,key){

}