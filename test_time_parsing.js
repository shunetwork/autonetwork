// 测试时间解析函数
function formatLogTime(timeStr) {
    if (!timeStr) return '-';
    
    // 处理日志时间戳格式 (如: "2025-10-21 10:59:14,928")
    let time;
    
    try {
        if (timeStr.includes(',')) {
            // 去掉毫秒部分，格式: "2025-10-21 10:59:14,928" -> "2025-10-21 10:59:14"
            const cleanTime = timeStr.split(',')[0];
            // 直接解析日期时间字符串
            time = new Date(cleanTime);
        } else {
            time = new Date(timeStr);
        }
        
        // 检查日期是否有效
        if (isNaN(time.getTime())) {
            // 如果无法解析，尝试ISO格式
            const parts = timeStr.split(' ');
            if (parts.length >= 2) {
                const datePart = parts[0];
                const timePart = parts[1].split(',')[0];
                time = new Date(`${datePart}T${timePart}`);
            }
        }
        
        // 如果仍然无效，返回原始字符串
        if (isNaN(time.getTime())) {
            return timeStr;
        }
        
        // 只显示日/月/年格式
        return time.toLocaleDateString('zh-CN', { 
            day: '2-digit', 
            month: '2-digit', 
            year: 'numeric' 
        });
    } catch (e) {
        // 如果出现任何错误，返回原始字符串
        return timeStr;
    }
}

// 测试用例
const testCases = [
    "2025-10-21 10:59:14,928",
    "2025-10-22 15:47:20,985",
    "2025-10-22 09:58:01,190",
    "2025-10-22 17:00:58,123"
];

console.log("测试时间解析函数:");
testCases.forEach(testCase => {
    const result = formatLogTime(testCase);
    console.log(`输入: ${testCase} -> 输出: ${result}`);
});
