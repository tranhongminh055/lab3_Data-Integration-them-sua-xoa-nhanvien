from flask import Flask, render_template, request, redirect, url_for, flash  # Import lớp Flask và các hàm hỗ trợ
from flask_sqlalchemy import SQLAlchemy  # Import SQLAlchemy để quản lý cơ sở dữ liệu bằng ORM
from sqlalchemy.exc import OperationalError  # Import lỗi kết nối cơ sở dữ liệu
import config  # Import cấu hình kết nối từ file config.py

app = Flask(__name__)  # Tạo đối tượng ứng dụng Flask
app.secret_key = "your_secret_key_here"  # Khóa bí mật dùng cho flash messages
app.config["SQLALCHEMY_DATABASE_URI"] = config.SQL_SERVER_CONN  # Cấu hình kết nối mặc định tới SQL Server
app.config["SQLALCHEMY_BINDS"] = {
    "default": config.SQL_SERVER_CONN,  # Bind mặc định kết nối tới SQL Server
    "mysql": config.MYSQL_CONN,  # Bind MySQL kết nối tới MySQL
}
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False  # Tắt tính năng theo dõi thay đổi để giảm overhead

db = SQLAlchemy(app)  # Khởi tạo đối tượng SQLAlchemy với Flask app

# Mô hình dữ liệu SQL Server
class HoSoNhanVienSQL(db.Model):
    __tablename__ = "HoSoNhanVien"  # Tên bảng trong SQL Server
    __bind_key__ = "default"  # Sử dụng kết nối bind mặc định

    MaNV = db.Column(db.Integer, primary_key=True, autoincrement=True)  # Khóa chính tự tăng
    HoTen = db.Column(db.String(100), nullable=False)  # Họ tên nhân viên
    NgaySinh = db.Column(db.Date)  # Ngày sinh nhân viên
    GioiTinh = db.Column(db.String(10))  # Giới tính
    DiaChi = db.Column(db.String(255))  # Địa chỉ
    SoDienThoai = db.Column(db.String(15))  # Số điện thoại
    Email = db.Column(db.String(100))  # Email
    NgayVaoLam = db.Column(db.Date)  # Ngày vào làm


# Mô hình dữ liệu MySQL
class HoSoNhanVienMySQL(db.Model):
    __tablename__ = "hosonhanvien"  # Tên bảng trong MySQL
    __bind_key__ = "mysql"  # Sử dụng kết nối bind MySQL

    MaNV = db.Column(db.Integer, primary_key=True, autoincrement=True)  # Khóa chính tự tăng
    HoTen = db.Column(db.String(100), nullable=False)  # Họ tên nhân viên
    NgaySinh = db.Column(db.Date)  # Ngày sinh nhân viên
    GioiTinh = db.Column(db.String(10))  # Giới tính
    DiaChi = db.Column(db.String(255))  # Địa chỉ
    SoDienThoai = db.Column(db.String(15))  # Số điện thoại
    Email = db.Column(db.String(100))  # Email
    NgayVaoLam = db.Column(db.Date)  # Ngày vào làm
    PhongBan = db.Column(db.String(500))  # Phòng ban
    ChucVu = db.Column(db.String(500))  # Chức vụ


class LuongNhanVien(db.Model):
    __tablename__ = "luongnhanvien"  # Tên bảng lương trong MySQL
    __bind_key__ = "mysql"  # Sử dụng kết nối bind MySQL

    MaLuong = db.Column(db.Integer, primary_key=True, autoincrement=True)  # Khóa chính lương
    MaNV = db.Column(db.Integer, db.ForeignKey("hosonhanvien.MaNV"))  # Khóa ngoại liên kết tới nhân viên MySQL
    ThangNam = db.Column(db.Date)  # Tháng năm lương
    LuongCoBan = db.Column(db.Float)  # Lương cơ bản
    PhuCap = db.Column(db.Float)  # Phụ cấp
    Thuong = db.Column(db.Float)  # Thưởng
    KhauTru = db.Column(db.Float)  # Khấu trừ
    LuongThucNhan = db.Column(db.Float)  # Lương thực nhận


@app.route("/")  # Route gốc
def index():
    return render_template("index.html")  # Trả về trang index.html


@app.route("/them-nhan-vien", methods=["GET", "POST"])  # Route thêm nhân viên
def them_nhan_vien():
    if request.method == "POST":  # Nếu form được submit bằng POST
        try:
            ho_ten = request.form.get("ho_ten")  # Lấy giá trị họ tên từ form
            ngay_sinh = request.form.get("ngay_sinh")  # Lấy giá trị ngày sinh
            gioi_tinh = request.form.get("gioi_tinh")  # Lấy giá trị giới tính
            dia_chi = request.form.get("dia_chi")  # Lấy giá trị địa chỉ
            so_dien_thoai = request.form.get("so_dien_thoai")  # Lấy số điện thoại
            email = request.form.get("email")  # Lấy email
            ngay_vao_lam = request.form.get("ngay_vao_lam")  # Lấy ngày vào làm
            phong_ban = request.form.get("phong_ban")  # Lấy phòng ban
            chuc_vu = request.form.get("chuc_vu")  # Lấy chức vụ

            nhan_vien_sql = HoSoNhanVienSQL(
                HoTen=ho_ten,
                NgaySinh=ngay_sinh,
                GioiTinh=gioi_tinh,
                DiaChi=dia_chi,
                SoDienThoai=so_dien_thoai,
                Email=email,
                NgayVaoLam=ngay_vao_lam,
            )  # Tạo đối tượng nhân viên SQL Server
            db.session.add(nhan_vien_sql)  # Thêm đối tượng vào phiên làm việc
            db.session.commit()  # Lưu dữ liệu vào SQL Server

            nhan_vien_mysql = HoSoNhanVienMySQL.query.get(nhan_vien_sql.MaNV)  # Tìm nhân viên MySQL theo MaNV
            if nhan_vien_mysql is None:
                nhan_vien_mysql = HoSoNhanVienMySQL(
                    MaNV=nhan_vien_sql.MaNV,
                    HoTen=ho_ten,
                    NgaySinh=ngay_sinh,
                    GioiTinh=gioi_tinh,
                    DiaChi=dia_chi,
                    SoDienThoai=so_dien_thoai,
                    Email=email,
                    NgayVaoLam=ngay_vao_lam,
                    PhongBan=phong_ban,
                    ChucVu=chuc_vu,
                )  # Tạo mới nhân viên MySQL nếu chưa tồn tại
            else:
                nhan_vien_mysql.HoTen = ho_ten
                nhan_vien_mysql.NgaySinh = ngay_sinh
                nhan_vien_mysql.GioiTinh = gioi_tinh
                nhan_vien_mysql.DiaChi = dia_chi
                nhan_vien_mysql.SoDienThoai = so_dien_thoai
                nhan_vien_mysql.Email = email
                nhan_vien_mysql.NgayVaoLam = ngay_vao_lam
                nhan_vien_mysql.PhongBan = phong_ban
                nhan_vien_mysql.ChucVu = chuc_vu
                # Cập nhật thông tin nhân viên MySQL nếu đã tồn tại

            db.session.add(nhan_vien_mysql)  # Thêm hoặc cập nhật đối tượng MySQL vào phiên làm việc
            db.session.commit()  # Lưu dữ liệu vào MySQL

            flash("Thêm nhân viên thành công!", "success")  # Hiển thị thông báo thành công
            return redirect(url_for("index"))  # Chuyển hướng về trang index
        except OperationalError as e:
            db.session.rollback()  # Quay lại phiên làm việc khi lỗi kết nối xảy ra
            flash(f"Lỗi kết nối cơ sở dữ liệu: Vui lòng kiểm tra SQL Server đang chạy", "error")
            return render_template("them_them_nhan_vien.htm")  # Hiển thị lại form nếu lỗi
        except Exception as e:
            db.session.rollback()  # Quay lại phiên làm việc khi có lỗi khác
            flash(f"Lỗi: {str(e)}", "error")
            return render_template("them_them_nhan_vien.htm")  # Hiển thị lại form nếu lỗi

    return render_template("them_them_nhan_vien.htm")  # Trả về form thêm nhân viên nếu yêu cầu GET


@app.route("/cap-nhat-nhan-vien/<int:manv>", methods=["GET", "POST"])  # Route hiển thị form cập nhật nhân viên theo MaNV
def cap_nhat_nhan_vien(manv):
    try:
        nhan_vien = HoSoNhanVienSQL.query.get(manv)  # Lấy nhân viên SQL Server theo MaNV
        if nhan_vien is None:
            flash("Nhân viên không tồn tại", "error")  # Thông báo nếu không tìm thấy nhân viên
            return redirect(url_for("index"))  # Quay về trang index

        nhan_vien_mysql = HoSoNhanVienMySQL.query.get(manv)  # Lấy dữ liệu MySQL bổ sung nếu có

        if request.method == "POST":  # Xử lý lưu cập nhật khi form submit
            ho_ten = request.form.get("ho_ten")
            ngay_sinh = request.form.get("ngay_sinh")
            gioi_tinh = request.form.get("gioi_tinh")
            dia_chi = request.form.get("dia_chi")
            so_dien_thoai = request.form.get("so_dien_thoai")
            email = request.form.get("email")
            ngay_vao_lam = request.form.get("ngay_vao_lam")
            phong_ban = request.form.get("phong_ban")
            chuc_vu = request.form.get("chuc_vu")

            nhan_vien.HoTen = ho_ten
            nhan_vien.NgaySinh = ngay_sinh
            nhan_vien.GioiTinh = gioi_tinh
            nhan_vien.DiaChi = dia_chi
            nhan_vien.SoDienThoai = so_dien_thoai
            nhan_vien.Email = email
            nhan_vien.NgayVaoLam = ngay_vao_lam
            db.session.add(nhan_vien)

            if nhan_vien_mysql is None:
                nhan_vien_mysql = HoSoNhanVienMySQL(
                    MaNV=manv,
                    HoTen=ho_ten,
                    NgaySinh=ngay_sinh,
                    GioiTinh=gioi_tinh,
                    DiaChi=dia_chi,
                    SoDienThoai=so_dien_thoai,
                    Email=email,
                    NgayVaoLam=ngay_vao_lam,
                    PhongBan=phong_ban,
                    ChucVu=chuc_vu,
                )
            else:
                nhan_vien_mysql.HoTen = ho_ten
                nhan_vien_mysql.NgaySinh = ngay_sinh
                nhan_vien_mysql.GioiTinh = gioi_tinh
                nhan_vien_mysql.DiaChi = dia_chi
                nhan_vien_mysql.SoDienThoai = so_dien_thoai
                nhan_vien_mysql.Email = email
                nhan_vien_mysql.NgayVaoLam = ngay_vao_lam
                nhan_vien_mysql.PhongBan = phong_ban
                nhan_vien_mysql.ChucVu = chuc_vu

            db.session.add(nhan_vien_mysql)
            db.session.commit()

            flash("Cập nhật nhân viên thành công.", "success")
            return redirect(url_for("index"))

        return render_template("cap_nhat_nhan_vien.html", nhan_vien=nhan_vien, nhan_vien_mysql=nhan_vien_mysql)  # Hiển thị form với dữ liệu nhân viên
    except OperationalError:
        flash("Lỗi kết nối cơ sở dữ liệu: Vui lòng kiểm tra SQL Server đang chạy", "error")
        return redirect(url_for("index"))
    except Exception as e:
        flash(f"Lỗi: {str(e)}", "error")
        return redirect(url_for("index"))


@app.route("/xoa-nhan-vien/<int:manv>")  # Route xóa nhân viên theo MaNV
def xoa_nhan_vien(manv):
    try:
        nhan_vien_sql = HoSoNhanVienSQL.query.get(manv)  # Lấy nhân viên SQL Server theo MaNV
        if nhan_vien_sql is None:
            flash("Nhân viên không tồn tại", "error")
            return redirect(url_for("index"))

        luong_nhan_vien = LuongNhanVien.query.filter_by(MaNV=manv).first()  # Kiểm tra tồn tại dữ liệu lương
        if luong_nhan_vien is not None:
            flash("Không thể xóa nhân viên vì đã tồn tại dữ liệu lương.", "error")
            return redirect(url_for("index"))  # Nếu có lương thì không xóa

        nhan_vien_mysql = HoSoNhanVienMySQL.query.get(manv)  # Lấy nhân viên MySQL cùng MaNV
        if nhan_vien_mysql is not None:
            db.session.delete(nhan_vien_mysql)  # Xóa nhân viên MySQL nếu tồn tại

        db.session.delete(nhan_vien_sql)  # Xóa nhân viên SQL Server
        db.session.commit()  # Lưu thay đổi xóa vào database

        flash("Xóa nhân viên thành công.", "success")
        return redirect(url_for("index"))
    except OperationalError:
        db.session.rollback()
        flash("Lỗi kết nối cơ sở dữ liệu: Vui lòng kiểm tra SQL Server đang chạy", "error")
        return redirect(url_for("index"))
    except Exception as e:
        db.session.rollback()
        flash(f"Lỗi: {str(e)}", "error")
        return redirect(url_for("index"))


@app.route("/in-danh-sach")  # Route hiển thị form in danh sách
def in_danh_sach():
    return render_template("in_danh_sach.html")  # Trả về template in_danh_sach.html


@app.route("/in-bang-luong")  # Route in bảng lương
def in_bang_luong():
    try:
        nhan_viens = HoSoNhanVienSQL.query.all()  # Lấy tất cả nhân viên từ SQL Server
        luong_nhan_vien = LuongNhanVien.query.all()  # Lấy tất cả dữ liệu lương từ MySQL

        data = []  # Danh sách kết hợp nhân viên và lương
        for nv in nhan_viens:
            luong = next((l for l in luong_nhan_vien if l.MaNV == nv.MaNV), None)  # Tìm lương tương ứng
            if luong:
                data.append((nv, luong))  # Thêm cặp nhân viên + lương vào danh sách

        return render_template("in_bang_luong.html", nhan_viens=data)  # Hiển thị template với dữ liệu
    except OperationalError:
        flash("Lỗi kết nối cơ sở dữ liệu: Vui lòng kiểm tra SQL Server đang chạy", "error")
        return redirect(url_for("index"))
    except Exception as e:
        flash(f"Lỗi: {str(e)}", "error")
        return redirect(url_for("index"))


if __name__ == "__main__":  # Chạy server khi file này được chạy trực tiếp
    app.run(debug=True)  # Khởi động Flask ở chế độ debug
