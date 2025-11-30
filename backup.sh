#!/bin/bash

# 数据库备份脚本

BACKUP_DIR="/root/quit_habit/backups"
DB_FILE="/root/quit_habit/instance/quit_habit.db"
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="$BACKUP_DIR/quit_habit_$DATE.db"

# 创建备份目录
mkdir -p "$BACKUP_DIR"

# 备份数据库
if [ -f "$DB_FILE" ]; then
    cp "$DB_FILE" "$BACKUP_FILE"
    echo "✅ 备份成功: $BACKUP_FILE"
    
    # 压缩备份文件
    gzip "$BACKUP_FILE"
    echo "✅ 已压缩: ${BACKUP_FILE}.gz"
    
    # 只保留最近 30 天的备份
    find "$BACKUP_DIR" -name "quit_habit_*.db.gz" -mtime +30 -delete
    echo "✅ 已清理 30 天前的备份"
    
    # 显示备份列表
    echo ""
    echo "📦 当前备份列表:"
    ls -lh "$BACKUP_DIR" | tail -n +2
else
    echo "❌ 数据库文件不存在: $DB_FILE"
    exit 1
fi
