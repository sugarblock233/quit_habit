from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from functools import wraps
from datetime import datetime, date, timedelta
from werkzeug.security import check_password_hash, generate_password_hash
from config import Config
from models import db, Habit, HabitRecord
import os

app = Flask(__name__)
app.config.from_object(Config)

# 初始化数据库
db.init_app(app)

# 创建所有表
with app.app_context():
    db.create_all()


# ==================== 安全装饰器 ====================

def login_required(f):
    """登录验证装饰器"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # 如果没有设置密码，不需要登录
        if not app.config.get('APP_PASSWORD'):
            return f(*args, **kwargs)
        
        # 检查是否已登录
        if not session.get('logged_in'):
            if request.path.startswith('/api/'):
                return jsonify({'error': '未登录', 'redirect': '/login'}), 401
            return redirect(url_for('login'))
        
        return f(*args, **kwargs)
    return decorated_function


# ==================== 认证路由 ====================

@app.route('/login', methods=['GET', 'POST'])
def login():
    """登录页面"""
    # 如果没有设置密码，直接跳转到首页
    if not app.config.get('APP_PASSWORD'):
        return redirect(url_for('index'))
    
    # 如果已经登录，直接跳转到首页
    if session.get('logged_in'):
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        data = request.get_json() if request.is_json else request.form
        password = data.get('password')
        
        if password == app.config.get('APP_PASSWORD'):
            session['logged_in'] = True
            session.permanent = True  # 使用持久化 session
            
            if request.is_json:
                return jsonify({'success': True, 'message': '登录成功'})
            return redirect(url_for('index'))
        else:
            if request.is_json:
                return jsonify({'success': False, 'error': '密码错误'}), 401
            return render_template('login.html', error='密码错误')
    
    return render_template('login.html')


@app.route('/logout')
def logout():
    """登出"""
    session.pop('logged_in', None)
    return redirect(url_for('login'))


# ==================== Web 页面路由 ====================

@app.route('/')
@login_required
def index():
    """主页 - 显示所有习惯列表"""
    return render_template('index.html')


@app.route('/habit/<int:habit_id>')
@login_required
def habit_detail(habit_id):
    """习惯详情页 - 显示日历视图"""
    return render_template('habit_detail.html', habit_id=habit_id)


# ==================== API 路由 ====================

@app.route('/api/habits', methods=['GET'])
@login_required
def get_habits():
    """获取所有习惯"""
    habits = Habit.query.order_by(Habit.created_at.desc()).all()
    
    result = []
    for habit in habits:
        habit_dict = habit.to_dict()
        habit_dict['consecutive_days'] = habit.get_consecutive_days()
        habit_dict['last_fail_date'] = habit.get_last_fail_date()
        result.append(habit_dict)
    
    return jsonify(result)


@app.route('/api/habits', methods=['POST'])
@login_required
def create_habit():
    """创建新习惯"""
    data = request.get_json()
    
    if not data or 'name' not in data:
        return jsonify({'error': '习惯名称不能为空'}), 400
    
    # 解析开始日期
    start_date_str = data.get('start_date')
    if start_date_str:
        try:
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
        except ValueError:
            return jsonify({'error': '日期格式错误，应为 YYYY-MM-DD'}), 400
    else:
        start_date = date.today()
    
    habit = Habit(
        name=data['name'],
        description=data.get('description', ''),
        start_date=start_date
    )
    
    db.session.add(habit)
    db.session.commit()
    
    return jsonify(habit.to_dict()), 201


@app.route('/api/habits/<int:habit_id>', methods=['GET'])
@login_required
def get_habit(habit_id):
    """获取单个习惯详情"""
    habit = Habit.query.get_or_404(habit_id)
    
    habit_dict = habit.to_dict()
    habit_dict['consecutive_days'] = habit.get_consecutive_days()
    habit_dict['last_fail_date'] = habit.get_last_fail_date()
    
    return jsonify(habit_dict)


@app.route('/api/habits/<int:habit_id>', methods=['DELETE'])
@login_required
def delete_habit(habit_id):
    """删除习惯"""
    habit = Habit.query.get_or_404(habit_id)
    db.session.delete(habit)
    db.session.commit()
    
    return jsonify({'message': '习惯已删除'}), 200


@app.route('/api/habits/<int:habit_id>/calendar', methods=['GET'])
@login_required
def get_habit_calendar(habit_id):
    """获取习惯的日历数据
    
    参数:
        year: 年份（默认当前年）
        month: 月份（默认当前月）
    """
    habit = Habit.query.get_or_404(habit_id)
    
    # 获取年月参数
    year = request.args.get('year', type=int, default=date.today().year)
    month = request.args.get('month', type=int, default=date.today().month)
    
    # 计算该月第一天和最后一天
    first_day = date(year, month, 1)
    if month == 12:
        last_day = date(year + 1, 1, 1) - timedelta(days=1)
    else:
        last_day = date(year, month + 1, 1) - timedelta(days=1)
    
    # 查询该月的所有失败记录
    records = HabitRecord.query.filter(
        HabitRecord.habit_id == habit_id,
        HabitRecord.date >= first_day,
        HabitRecord.date <= last_day
    ).all()
    
    # 构建日历数据
    calendar_data = []
    current_date = first_day
    
    # 获取失败日期的集合
    fail_dates = {record.date: record for record in records}
    
    while current_date <= last_day:
        day_data = {
            'date': current_date.isoformat(),
            'day': current_date.day,
            'status': 'success'  # 默认成功
        }
        
        # 如果这天有失败记录
        if current_date in fail_dates:
            record = fail_dates[current_date]
            day_data['status'] = 'fail'
            day_data['reason'] = record.reason
            day_data['record_id'] = record.id
        
        # 如果日期在习惯开始日期之前，标记为未开始
        if current_date < habit.start_date:
            day_data['status'] = 'not-started'
        
        # 如果日期是未来，标记为未来
        if current_date > date.today():
            day_data['status'] = 'future'
        
        calendar_data.append(day_data)
        current_date += timedelta(days=1)
    
    return jsonify({
        'year': year,
        'month': month,
        'days': calendar_data,
        'habit': habit.to_dict()
    })


@app.route('/api/habits/<int:habit_id>/records', methods=['POST'])
@login_required
def mark_fail(habit_id):
    """标记某天失败"""
    habit = Habit.query.get_or_404(habit_id)
    data = request.get_json()
    
    if not data or 'date' not in data:
        return jsonify({'error': '日期不能为空'}), 400
    
    if not data.get('reason'):
        return jsonify({'error': '失败原因不能为空'}), 400
    
    # 解析日期
    try:
        fail_date = datetime.strptime(data['date'], '%Y-%m-%d').date()
    except ValueError:
        return jsonify({'error': '日期格式错误，应为 YYYY-MM-DD'}), 400
    
    # 检查日期是否在习惯开始日期之后
    if fail_date < habit.start_date:
        return jsonify({'error': '不能标记习惯开始之前的日期'}), 400
    
    # 检查日期是否是未来
    if fail_date > date.today():
        return jsonify({'error': '不能标记未来日期'}), 400
    
    # 检查是否已存在记录
    existing_record = HabitRecord.query.filter_by(
        habit_id=habit_id,
        date=fail_date
    ).first()
    
    if existing_record:
        # 更新现有记录
        existing_record.reason = data['reason']
        db.session.commit()
        return jsonify(existing_record.to_dict()), 200
    else:
        # 创建新记录
        record = HabitRecord(
            habit_id=habit_id,
            date=fail_date,
            status='fail',
            reason=data['reason']
        )
        db.session.add(record)
        db.session.commit()
        return jsonify(record.to_dict()), 201


@app.route('/api/records/<int:record_id>', methods=['PUT'])
@login_required
def update_record(record_id):
    """更新失败记录"""
    record = HabitRecord.query.get_or_404(record_id)
    data = request.get_json()
    
    if not data or 'reason' not in data:
        return jsonify({'error': '失败原因不能为空'}), 400
    
    record.reason = data['reason']
    db.session.commit()
    
    return jsonify(record.to_dict())


@app.route('/api/records/<int:record_id>', methods=['DELETE'])
@login_required
def delete_record(record_id):
    """删除失败记录（将该天改回成功）"""
    record = HabitRecord.query.get_or_404(record_id)
    db.session.delete(record)
    db.session.commit()
    
    return jsonify({'message': '记录已删除，该天已恢复为成功状态'}), 200


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
