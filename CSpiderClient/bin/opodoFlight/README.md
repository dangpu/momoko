#opodo 文档

##get_city_code.py

以 city.txt 为原始数据，读取其中的城市代码，用每个城市的城市代码为 searchKey 请求链接：
> http://www.opodo.co.uk/opodo/flights/resolveGeoApiLocation?
>query=locale=en_GB;searchMainProductType=FLIGHT;
website=OPUK;searchKey=%s;departureOrArrival=DEPARTURE

得到该城市代码对应的 suggestion 页面， 载入该页面的 json 数据，拼接 cityName，countryName 和 iataCode 键对应的值，再用城市代码和拼接成的值组成新的字典中的键值对。

>eg:	‘BJS’:‘Beijing, China [BJS]’

最终生成 citycode_common.py 文件。



