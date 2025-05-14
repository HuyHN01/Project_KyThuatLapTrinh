from flask import Blueprint, render_template, request

main_bp = Blueprint('main_routes', __name__) # Bỏ template_folder nếu base_layout và các trang con cùng cấp trong app/templates

@main_bp.route('/')
@main_bp.route('/index')
def index():
    # Tạm thời render một trang trống hoặc trang danh sách bài hát (sẽ làm ở 3.2)
    # Để kiểm tra base_layout, bạn có thể tạo một template đơn giản kế thừa từ nó
    return render_template('home_placeholder.html', title="Trang Chủ")

@main_bp.route('/search')
def search():
    query = request.args.get('query', '')
    return render_template('search_results_placeholder.html', title=f"Kết quả cho: {query}", search_query=query)
