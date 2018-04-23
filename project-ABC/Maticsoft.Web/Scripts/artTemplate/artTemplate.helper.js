// artTemplate 辅助方法：

/**
 * 日期格式化 支持输出星期几 （使用如：new Date().format('yyyy年mm月dd日 WWW hh:ii:ss')）
 * 月(M)、日(d)、12小时(h)、24小时(H)、分(m)、秒(s)、周(E)、季度(q) 可以用 1-2 个占位符
 * 年(y)可以用 1-4 个占位符，毫秒(S)只能用 1 个占位符(是 1-3 位的数字)
 * eg:
 * (new Date()).pattern("yyyy-mm-dd hh:ii:ss.S") ==> 2006-07-02 08:09:04.423
 * (new Date()).pattern("yyyy-mm-dd W HH:ii:ss") ==> 2009-03-10 二 20:09:04
 * (new Date()).pattern("yyyy-mm-dd WW hh:ii:ss") ==> 2009-03-10 周二 08:09:04
 * (new Date()).pattern("yyyy-mm-dd WWW hh:ii:ss") ==> 2009-03-10 星期二 08:09:04
 * (new Date()).pattern("yy-m-d h:m:s.S") ==> 09-7-2 8:9:4.18
 */
template.helper('dateFormat', function (dateStr, format) {
    var date;
	if ((/(\d{13})/).test(dateStr)) { // 针对 js 时间戳
		date = new Date(dateStr);
	}
	else {
		date = new Date(dateStr.replace(/\-/g, '/'));		
	}
	var map = {
		"m+" : date.getMonth() + 1,                   // 月份
		"d+" : date.getDate(),                        // 日
		"h+" : date.getHours(),                       // 小时
		"H+" : date.getHours() % 12 === 0 ? 12 : date.getHours() % 12, // 12小时制
		"i+" : date.getMinutes(),                     // 分
		"s+" : date.getSeconds(),                     // 秒
		"q+" : Math.floor((date.getMonth() + 3) / 3), // 季度
		"S"  : date.getMilliseconds()                 // 毫秒
	};
	var week = {
		"0": "\u65e5",
		"1": "\u4e00",
		"2": "\u4e8c",
		"3": "\u4e09",
		"4": "\u56db",
		"5": "\u4e94",
		"6": "\u516d"
	};
	if (/(y+)/.test(format)) {
		format = format.replace(RegExp.$1, (date.getFullYear() + "").substr(4 - RegExp.$1.length));
	}
	if (/(W+)/.test(format)) {
		format = format.replace(RegExp.$1, ((RegExp.$1.length > 1) ? (RegExp.$1.length > 2 ? "\u661f\u671f": "\u5468") : "") + week[date.getDay() + ""]);
	}
	for (var k in map) {
		if (new RegExp("(" + k + ")").test(format)) {
			format = format.replace(RegExp.$1, (RegExp.$1.length == 1) ? (map[k]) : (("00" + map[k]).substr(("" + map[k]).length)));
		}
	}
	return format;
});
/**
 * 格式化 输出 两位小数
 */
template.helper('formatNumber', function (digitStr, pad) {
	if (/^\d$/.test(digitStr)) {
		return digitStr; // 整数直接返回
	}
	return parseFloat(digitStr, 10).toFixed(parseInt(pad, 10));
});