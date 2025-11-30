from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class Habit(db.Model):
    """习惯表"""
    __tablename__ = 'habits'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    start_date = db.Column(db.Date, nullable=False, default=datetime.utcnow().date)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # 关系：一个习惯对应多条记录
    records = db.relationship('HabitRecord', backref='habit', lazy=True, cascade='all, delete-orphan')
    
    def to_dict(self):
        """转换为字典格式"""
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'start_date': self.start_date.isoformat(),
            'created_at': self.created_at.isoformat()
        }
    
    def get_consecutive_days(self):
        """计算连续成功天数（从今天往前推算）"""
        from datetime import date, timedelta
        
        today = date.today()
        consecutive = 0
        current_date = today
        
        # 从今天开始往前检查
        while current_date >= self.start_date:
            # 查询这一天是否有失败记录
            record = HabitRecord.query.filter_by(
                habit_id=self.id,
                date=current_date,
                status='fail'
            ).first()
            
            if record:
                # 遇到失败记录，停止计数
                break
            
            consecutive += 1
            current_date -= timedelta(days=1)
        
        return consecutive
    
    def get_last_fail_date(self):
        """获取最近一次失败日期"""
        record = HabitRecord.query.filter_by(
            habit_id=self.id,
            status='fail'
        ).order_by(HabitRecord.date.desc()).first()
        
        return record.date.isoformat() if record else None


class HabitRecord(db.Model):
    """习惯记录表（仅记录失败）"""
    __tablename__ = 'habit_records'
    
    id = db.Column(db.Integer, primary_key=True)
    habit_id = db.Column(db.Integer, db.ForeignKey('habits.id'), nullable=False)
    date = db.Column(db.Date, nullable=False)
    status = db.Column(db.String(20), default='fail')  # 只记录 'fail'
    reason = db.Column(db.Text)  # 失败原因
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # 唯一约束：同一习惯同一天只能有一条记录
    __table_args__ = (db.UniqueConstraint('habit_id', 'date', name='_habit_date_uc'),)
    
    def to_dict(self):
        """转换为字典格式"""
        return {
            'id': self.id,
            'habit_id': self.habit_id,
            'date': self.date.isoformat(),
            'status': self.status,
            'reason': self.reason,
            'created_at': self.created_at.isoformat()
        }
