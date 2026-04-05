from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import OperationalError
import config  # Import file config.py

app = Flask(__name__)
app.secret_key = "your_secret_key_here"  # For flash messages
app.config["SQLALCHEMY_DATABASE_URI"] = config.SQL_SERVER_CONN
app.config["SQLALCHEMY_BINDS"] = {
    "default": config.SQL_SERVER_CONN,
    "mysql": config.MYSQL_CONN,
}
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)

# Mô hình dữ liệu SQL Server
class HoSoNhanVienSQL(db.Model):
    __tablename__ = "HoSoNhanVien"
    __bind_key__ = "default"

    MaNV = db.Column(db.Integer, primary_key=True, autoincrement=True)
    HoTen = db.Column(db.String(100), nullable=False)
    NgaySinh = db.Column(db.Date)
    GioiTinh = db.Column(db.String(10))
    DiaChi = db.Column(db.String(255))
    SoDienThoai = db.Column(db.String(15))
    Email = db.Column(db.String(100))
    NgayVaoLam = db.Column(db.Date)


# Mô hình dữ liệu MySQL
class HoSoNhanVienMySQL(db.Model):
    __tablename__ = "hosonhanvien"
    __bind_key__ = "mysql"

    MaNV = db.Column(db.Integer, primary_key=True, autoincrement=True)
    HoTen = db.Column(db.String(100), nullable=False)
    NgaySinh = db.Column(db.Date)
    GioiTinh = db.Column(db.String(10))
    DiaChi = db.Column(db.String(255))
    SoDienThoai = db.Column(db.String(15))
    Email = db.Column(db.String(100))
    NgayVaoLam = db.Column(db.Date)
    PhongBan = db.Column(db.String(500))
    ChucVu = db.Column(db.String(500))


class LuongNhanVien(db.Model):
    __tablename__ = "luongnhanvien"
    __bind_key__ = "mysql"

    MaLuong = db.Column(db.Integer, primary_key=True, autoincrement=True)
    MaNV = db.Column(db.Integer, db.ForeignKey("hosonhanvien.MaNV"))
    ThangNam = db.Column(db.Date)
    LuongCoBan = db.Column(db.Float)
    PhuCap = db.Column(db.Float)
    Thuong = db.Column(db.Float)
    KhauTru = db.Column(db.Float)
    LuongThucNhan = db.Column(db.Float)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/them-nhan-vien", methods=["GET", "POST"])
def them_nhan_vien():
    if request.method == "POST":
        try:
            ho_ten = request.form.get("ho_ten")
            ngay_sinh = request.form.get("ngay_sinh")
            gioi_tinh = request.form.get("gioi_tinh")
            dia_chi = request.form.get("dia_chi")
            so_dien_thoai = request.form.get("so_dien_thoai")
            email = request.form.get("email")
            ngay_vao_lam = request.form.get("ngay_vao_lam")
            phong_ban = request.form.get("phong_ban")
            chuc_vu = request.form.get("chuc_vu")

            nhan_vien_sql = HoSoNhanVienSQL(
                HoTen=ho_ten,
                NgaySinh=ngay_sinh,
                GioiTinh=gioi_tinh,
                DiaChi=dia_chi,
                SoDienThoai=so_dien_thoai,
                Email=email,
                NgayVaoLam=ngay_vao_lam,
            )
            db.session.add(nhan_vien_sql)
            db.session.commit()

            nhan_vien_mysql = HoSoNhanVienMySQL.query.get(nhan_vien_sql.MaNV)
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

            flash("Thêm nhân viên thành công!", "success")
            return redirect(url_for("index"))
        except OperationalError as e:
            db.session.rollback()
            flash(f"Lỗi kết nối cơ sở dữ liệu: Vui lòng kiểm tra SQL Server đang chạy", "error")
            return render_template("them_them_nhan_vien.htm")
        except Exception as e:
            db.session.rollback()
            flash(f"Lỗi: {str(e)}", "error")
            return render_template("them_them_nhan_vien.htm")

    return render_template("them_them_nhan_vien.htm")


@app.route("/in-bang-luong")
def in_bang_luong():
    try:
        nhan_viens = HoSoNhanVienSQL.query.all()
        luong_nhan_vien = LuongNhanVien.query.all()

        data = []
        for nv in nhan_viens:
            luong = next((l for l in luong_nhan_vien if l.MaNV == nv.MaNV), None)
            if luong:
                data.append((nv, luong))

        return render_template("in_bang_luong.html", nhan_viens=data)
    except OperationalError:
        flash("Lỗi kết nối cơ sở dữ liệu: Vui lòng kiểm tra SQL Server đang chạy", "error")
        return redirect(url_for("index"))
    except Exception as e:
        flash(f"Lỗi: {str(e)}", "error")
        return redirect(url_for("index"))


if __name__ == "__main__":
    app.run(debug=True)
