from lxml import etree
import re
#
# str = '''
# <div id="prodDetails" class="a-section">    <h2>
#                           Product information </h2>
#                        <div class="a-row a-spacing-top-base"> <div class="a-column a-span6"> <div class="a-row a-spacing-base">   <div class="a-section table-padding"> <table id="productDetails_detailBullets_sections1" class="a-keyvalue prodDetTable" role="presentation">          <tbody><tr> <th class="a-color-secondary a-size-base prodDetSectionEntry"> Material </th>  <td class="a-size-base prodDetAttrValue"> Stainless Steel </td> </tr>            <tr> <th class="a-color-secondary a-size-base prodDetSectionEntry"> Brand </th>  <td class="a-size-base prodDetAttrValue"> Made In </td> </tr>            <tr> <th class="a-color-secondary a-size-base prodDetSectionEntry"> Item Diameter </th>  <td class="a-size-base prodDetAttrValue"> 12 Inches </td> </tr>            <tr> <th class="a-color-secondary a-size-base prodDetSectionEntry"> Color </th>  <td class="a-size-base prodDetAttrValue"> Graphite </td> </tr>            <tr> <th class="a-color-secondary a-size-base prodDetSectionEntry"> Has Nonstick Coating </th>  <td class="a-size-base prodDetAttrValue"> Yes </td> </tr>            <tr> <th class="a-color-secondary a-size-base prodDetSectionEntry"> Is Oven Safe </th>  <td class="a-size-base prodDetAttrValue"> Yes </td> </tr>            <tr> <th class="a-color-secondary a-size-base prodDetSectionEntry"> Package Dimensions </th>  <td class="a-size-base prodDetAttrValue"> 21.4 x 13.4 x 3.9 inches </td> </tr>            <tr> <th class="a-color-secondary a-size-base prodDetSectionEntry"> Item Weight </th>  <td class="a-size-base prodDetAttrValue"> 4.44 pounds </td> </tr>            <tr> <th class="a-color-secondary a-size-base prodDetSectionEntry"> ASIN </th>  <td class="a-size-base prodDetAttrValue"> B09S15GJ8B </td> </tr>                          <tr> <th class="a-color-secondary a-size-base prodDetSectionEntry"> Country of Origin </th>  <td class="a-size-base prodDetAttrValue"> Italy </td> </tr>              <tr>   <th class="a-color-secondary a-size-base prodDetSectionEntry">Customer Reviews</th>  <td class="a-size-base">   <style type="text/css">
#     /*
#     * Fix for UDP-1061. Average customer reviews has a small extra line on hover
#     * https://omni-grok.amazon.com/xref/src/appgroup/websiteTemplates/retail/SoftlinesDetailPageAssets/udp-intl-lock/src/legacy.css?indexName=WebsiteTemplates#40
#     */
#     .noUnderline a:hover {
#         text-decoration: none;
#     }
# </style>
#
#                    <div id="averageCustomerReviews" data-asin="B09S15GJ8B" data-ref="dpx_acr_pop_">
#                           <span class="a-declarative" data-action="acrStarsLink-click-metrics" data-csa-c-type="widget" data-csa-c-func-deps="aui-da-acrStarsLink-click-metrics" data-acrstarslink-click-metrics="{}" data-csa-c-id="8xjxyn-5ozmvq-z7uf10-3y5ec">     <span id="acrPopover" class="reviewCountTextLinkedHistogram noUnderline" title="4.8 out of 5 stars">
#         <span class="a-declarative" data-action="a-popover" data-csa-c-type="widget" data-csa-c-func-deps="aui-da-a-popover" data-a-popover="{&quot;max-width&quot;:&quot;700&quot;,&quot;closeButton&quot;:&quot;false&quot;,&quot;position&quot;:&quot;triggerBottom&quot;,&quot;url&quot;:&quot;/gp/customer-reviews/widgets/average-customer-review/popover/ref=dpx_acr_pop_?contextId=dpx&amp;asin=B09S15GJ8B&quot;}" data-csa-c-id="ju15yr-mjplik-apscbl-7viuon"> <a href="javascript:void(0)" role="button" class="a-popover-trigger a-declarative">  <i class="a-icon a-icon-star a-star-5"><span class="a-icon-alt">4.8 out of 5 stars</span></i>  <i class="a-icon a-icon-popover"></i></a> </span> <span class="a-letter-space"></span> </span>
#
#        </span> <span class="a-letter-space"></span>             <span class="a-declarative" data-action="acrLink-click-metrics" data-csa-c-type="widget" data-csa-c-func-deps="aui-da-acrLink-click-metrics" data-acrlink-click-metrics="{}" data-csa-c-id="rpox4h-1ch6uu-mm6mp9-azx1id"> <a id="acrCustomerReviewLink" class="a-link-normal" href="#customerReviews"> <span id="acrCustomerReviewText" class="a-size-base">77 ratings</span> </a> </span> <script type="text/javascript">
#                     P.when('A', 'ready').execute(function(A) {
#                         A.declarative('acrLink-click-metrics', 'click', { "allowLinkDefault" : true }, function(event){
#                             if(window.ue) {
#                                 ue.count("acrLinkClickCount", (ue.count("acrLinkClickCount") || 0) + 1);
#                             }
#                         });
#                     });
#                 </script>
#                  <script type="text/javascript">
#             P.when('A', 'cf').execute(function(A) {
#                 A.declarative('acrStarsLink-click-metrics', 'click', { "allowLinkDefault" : true },  function(event){
#                     if(window.ue) {
#                         ue.count("acrStarsLinkWithPopoverClickCount", (ue.count("acrStarsLinkWithPopoverClickCount") || 0) + 1);
#                     }
#                 });
#             });
#         </script>
#
#            </div>
#       <br> 4.8 out of 5 stars </td> </tr>                <tr> <th class="a-color-secondary a-size-base prodDetSectionEntry"> Best Sellers Rank </th> <td> <span>  <span>#5,400 in Kitchen &amp; Dining (<a href="/gp/bestsellers/kitchen/ref=pd_zg_ts_kitchen">See Top 100 in Kitchen &amp; Dining</a>)</span> <br>  <span>#28 in <a href="/gp/bestsellers/kitchen/289829/ref=pd_zg_hrsr_kitchen">Skillets</a></span> <br>  </span> </td> </tr>               <tr> <th class="a-color-secondary a-size-base prodDetSectionEntry"> Date First Available </th>  <td class="a-size-base prodDetAttrValue"> February 10, 2022 </td> </tr>      </tbody></table> </div>  </div> </div> <div class="a-column a-span6 a-span-last">      <div class="a-row a-spacing-base"> <h1 class="a-size-medium a-spacing-small secHeader"> Warranty &amp; Support </h1>  <div class="a-section table-padding">    <strong>Product Warranty:</strong> For warranty information about this product, please <a href="/gp/feature.html/ref=dp_warranty_request_3P?docId=1002406021" target="_blank">click here</a>  </div> </div>  <div class="a-row">       <div class="a-section"> <h1 class="a-size-medium a-spacing-small secHeader"> Feedback </h1> <div class="a-section table-padding"> <div class="a-row">       </div><div class="a-row">                 <div id="pricingFeedbackDiv">
#                 <span class="a-declarative" data-action="a-popover" data-csa-c-type="widget" data-csa-c-func-deps="aui-da-a-popover" data-a-popover="{&quot;closeButton&quot;:&quot;true&quot;,&quot;closeButtonLabel&quot;:&quot;Dismiss&quot;,&quot;name&quot;:&quot;pricingFeedbackPopup&quot;,&quot;width&quot;:&quot;450&quot;,&quot;activate&quot;:&quot;onclick&quot;,&quot;header&quot;:&quot;Tell Us About a Lower Price&quot;,&quot;position&quot;:&quot;triggerLeft&quot;,&quot;popoverLabel&quot;:&quot;Tell Us About a Lower Price&quot;,&quot;url&quot;:&quot;/gp/pdp/pf/pricingFeedbackForm.html/ref=_pfdpb?ie=UTF8&amp;PREFIX=ns_JY0ZSEJZ8VKKZJKCJQT4_&amp;ASIN=B09S15GJ8B&amp;from=product-detailencodeURI('&amp;originalURI=' + window.location.pathname)&quot;}" data-csa-c-id="9ici3s-mm1oyy-3ggmpt-ua1g2n"> Would you like to  <b><a href="javascript:void(0)" role="button" class="a-popover-trigger a-declarative">tell us about a lower price?<i class="a-icon a-icon-popover"></i></a></b>
#                 </span> </div>   </div><table id="productDetails_feedback_sections" class="a-keyvalue prodDetTable" role="presentation">   </table> </div> </div>   </div> </div> </div>     </div>'''
# pattern = '<script[\s\S]*</script>'
# str = re.sub(pattern,'',str)
# pattern = '<style[\s\S]*</style>'
# str = re.sub(pattern,'',str)
# #print(str)
# selector = etree.HTML(str)
# spans = selector.xpath('//ul//li//span[@class="a-list-item"]')
# if len(spans) == 0:
#     spans = selector.xpath('//tbody//tr')
#
# replace_arrs = ['\u200f','\u200e',':']
#
# product_dimensions = '#NA'
# weight = '#NA'
# date_first_available = '#NA'
# asin = '#NA'
# rank = '#NA'
# cat = '#NA'
# review_counts = '#NA'
# ratings = '#NA'
#
# for span in spans:
#     texts = span.xpath('.//text()')
#     for replace_arr in replace_arrs:
#         texts = [i.replace(replace_arr,"").strip() for i in texts if i != '']
#     print(texts)
#     if texts[0].find('Product Dimensions') != -1 or texts[0].find('Package Dimensions') != -1:
#         if texts[0].find(';') != -1:
#             product_dimensions = texts[1].split(";")[0]
#             weight = texts[1].split(";")[1]
#         else:
#             product_dimensions = texts[1]
#     if texts[0].find('Item Weight') != -1:
#         weight = texts[1]
#     if texts[0].find('Date First Available') != -1:
#         date_first_available = texts[1]
#     if texts[0].find('ASIN') != -1:
#         asin = texts[1]
#     if texts[0].find('Best Sellers Rank') != -1:
#         rank = texts[1].split('in')[0].replace('#', '').replace(',', '').strip()
#         cat = texts[1].split(' in ')[-1].replace("(","").strip()
#     if texts[0].find('Customer Reviews') != -1:
#         ratings = texts[1].replace(" out of 5 stars", '').strip()
#         review_counts = texts[-1].replace('ratings', '').strip()
#
# print([product_dimensions,weight,date_first_available,asin,rank,cat,review_counts,ratings])
for page in range(1,20):
    print(page)