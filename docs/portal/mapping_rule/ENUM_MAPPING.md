ở file md này, tôi sẽ trình bày các enum cần có để kiểm soát input chặt chẽ hơn khi user upload file excel. nếu họ để trống hoặc nhập sai giá trị, hệ thống sẽ cảnh báo lỗi ngay tại bước validate, tránh lỗi downstream khi xử lý dữ liệu.

1. Channel (NOT NULL) cho tất cả các loại bảo hiểm --> 'programCodeMiningChannel' (đã xử lý)
ENUM:
- DSA
- DSA/Renew
- DSA_NEO
- TSA
- Renew
- CTV_TSA (TSA 2)
- CTV_TSA (TSA 2)/Renew
- HO
- Digital
- Referral

2. Hình thức thanh toán (hiện tại đang NULLABLE --> cần sửa lại thành NOT NULL) --> 'termsFeePaymentMethod' (chưa xử lý)
ENUM:
- OCB
- Payoo
- Bảo Kim
- VietcomBank
- Nhà bảo hiểm
- Affina
==> Thì ở bước này bạn có thể check chuỗi xem có thuộc 1 trong các giá trị trên không, nếu không sẽ trả về lỗi validate ngay tại bước này. Nếu để trống cũng trả về lỗi vì đã set NOT NULL. ví dụ trong excel đang lưu là "Nhà BH" thì bạn có thể map "Nhà BH" thành "Nhà bảo hiểm" trước khi validate, hoặc bạn có thể yêu cầu user phải nhập đúng giá trị "Nhà bảo hiểm" trong excel để tránh lỗi mapping. Tùy vào mức độ strict bạn muốn áp dụng cho dữ liệu đầu vào ==> tương tự các giá trị còn lại

3. Nhà cung cấp bảo hiểm (NOT NULL) --> 'companyProviderName' (chưa xử lý ENUM)
Bảo hiểm du lịch:
- AAA
- AAA Thủ Đức
- Bảo Minh
- Bảo Minh Bến Thành
- Bảo Việt
- BHV
- VBI
- LIBERTY

Bảo hiểm ô tô:
- AAA
- AAA Thủ Đức
- Bảo Minh
- Bảo Minh Bến Nghé
- Bảo Minh Bến Thành
- Bảo Việt
- BSH
- DBV Nghệ An
- LIBERTY
- MIC
- PJICO
- PTI
- PVI Digital
- PVI Đồng Khởi
- PVI Gia Định
- Tasco
- VNI

Bảo hiểm rủi ro:
- AAA
- Bảo Minh Bến Nghé
- Bảo Minh Bến Thành
- Bảo Việt
- LIBERTY
- MIC
- PVI Đồng Khởi
- PVI Gia Định
- QBE

Bảo hiểm sức khỏe:
- AAA
- Bảo Minh
- Bảo Minh Bến Nghé
- Bảo Minh Bến Thành
- Bảo Việt
- BHV
- BSH
- GIC
- LIBERTY
- MIC
- OPES
- Pacific Cross
- PCV
- PTI
- PVI
- PVI Đồng Khởi
- PVI Gia Định
- TCGI
- VBI

Bảo hiểm xe máy:
- AAA
- DBV Nghệ An
- BSH
- PVI Digital

Bảo hiểm y tế xã hội:
- PVI Digital

4. Sản phẩm (NOT NULL) --> hiện tại đang map vào field 'majorName' ==> đây là field map sai, cần map vào field 'programName' mới đúng (chưa xử lý ENUM)
NOTE: Quan trọng, hiện tại tất cả các loại bảo hiểm đang map sai field cho sản phẩm là majorName. Field cần map đúng là 'programName' cho tất cả các loại bảo hiểm luôn
Bảo hiểm du lịch:
- Bảo hiểm du lịch Trong nước
- Bảo hiểm người Việt Nam du lịch nước ngoài
- Bảo hiểm người nước ngoài du lịch Việt Nam
- Bảo hiểm du lịch Bảo Minh
- Bảo hiểm du lịch Bảo Việt
- Bảo hiểm du lịch VBI
- Bảo hiểm du lịch BHV
- Bảo hiểm du lịch Liberty
- Bảo hiểm du lịch AAATD
- Bảo hiểm du lịch Nước ngoài

Bảo hiểm ô tô:
- BHVCOTO_AAATD
- Bảo hiểm Lái phụ xe và người ngồi trên xe ô tô, TNDS tự nguyện
- Bảo hiểm Trách nhiệm Dân sự ô tô
- BHVCOTO_PVI
- BHVCOTO_PVI_GĐ
- BHVCOTO_DBV Nghệ An_Xe taxi
- BHVCOTO_Bảo Minh
- BHVCOTO_Bảo Minh Bến Nghé
- BHVCOTO_Bảo Việt
- Bảo hiểm vật chất xe Ô tô
- BHVCOTO_BSH
- Bảo hiểm Vật chất xe ô tô
- BHVCOTO_PJICO
- BHVCOTO_PJICO dưới 600
- BHVCOTO_PJICO trên 800
- BHVCOTO_PJICO từ 600 đến dưới 800
- BHVCOTO_PTI
- BHVCOTO_PVI_Digital
- BHVCOTO_PVI_ĐK dưới 500
- BHVCOTO_PVI_ĐK trên 1000
- BHVCOTO_PVI_ĐK từ 500 đến dưới 700
- BHVCOTO_PVI_ĐK từ 700 đến dưới 1000
- BHVCOTO_Bảo Minh Bến Thành
- BHVCOTO_VNI
- Bảo hiểm Lái phụ xe và người ngồi trên xe ô tô, TNDS tự nguyện_Xe còn lại
- Bảo hiểm Lái phụ xe và người ngồi trên xe ô tô, TNDS tự nguyện_Ô tô dưới 16 chỗ, xe tải dưới 3 tấn
- Bảo hiểm Trách nhiệm Dân sự ô tô_Xe còn lại
- Bảo hiểm Trách nhiệm Dân sự ô tô_Ô tô dưới 16 chỗ, xe tải dưới 3 tấn
- BHVCOTO_PTI >= 500
- BHVCOTO_PTI dưới 500
- BHVCOTO_Liberty
- BHVCOTO_Liberty_new
- BHVCOTO_Liberty_renew
- BHVCOTO_MIC
- BHVCOTO_Tasco
- BHVCOTO_DBV Nghệ An_Xe cơ giới khác

Bảo hiểm rủi ro:
- Bảo hiểm cháy, nổ bắt buộc_CAT1,2
- Bảo hiểm cháy, nổ bắt buộc_CAT3
- Bảo hiểm cháy, nổ bắt buộc_CAT4
- Bảo hiểm cháy, nổ bắt buộc_CAT5
- Bảo hiểm cháy, nổ bắt buộc_CAT3,4
- Bảo hiểm cháy, nổ bắt buộc
- Hỏa hoạn và các rủi ro đặc biệt_CAT1,2
- Hỏa hoạn và các rủi ro đặc biệt_CAT3
- Hỏa hoạn và các rủi ro đặc biệt_CAT4
- Hỏa hoạn và các rủi ro đặc biệt_CAT5
- Bảo Hiểm Nhà Tư Nhân
- Bảo hiểm mọi rủi ro xây dựng và lắp đặt
- Bh mọi rủi ro lắp đặt & TN bên thứ 3
- BẢO HIỂM MỌI RỦI RO XÂY DỰNG VÀ LẮP ĐẶT
- Bảo hiểm Mọi rủi ro xây dựng và trách nhiệm đối với bên thứ ba
- Bảo hiểm bắt buộc Trách nhiệm nghề nghiệp tư vấn đầu tư xây dựng
- Bảo hiểm cháy và các rủi ro đặc biệt
- Bảo hiểm hỏa hoạn và các rủi ro đặc biệt (tùy loại rủi ro, số tiền bảo hiểm)
- Bảo hiểm toàn diện nhà tư nhân
- Bảo hiểm trách nhiệm công cộng
- Đơn mọi rủi ro tài sản
- Trách nhiệm nghề nghiệp
- BH mọi rủi ro tài sản
- Bảo hiểm nhà An Gia Phát
- Mọi rủi ro tài sản
- Bảo hiểm mọi rủi ro về tiền
- BẢO HIỂM TRÁCH NHIỆM

Bảo hiểm sức khỏe:
- SKTA_renew
- An Sinh Thịnh Vượng
- BV_Cl10
- Bảo hiểm Tai nạn
- Bảo hiểm sức khỏe doanh nghiệp
- B-One
- B-One_new
- B-One_renew
- Bestlife
- Bestlife_new
- Bestlife_renew
- SKNC_new
- SKNC_renew
- Tai nạn cá nhân GIC
- Foundation (Toàn Mỹ)_new
- Foundation (Toàn Mỹ)_renew
- Health first_new
- Health first_renew
- Health up_new
- Health up_renew
- Master M1+
- Master M2
- Master M3
- An Gia Phát
- Bảo hiểm An Gia Phát
- Bảo hiểm tai nạn cá nhân
- Sức khỏe toàn diện cá nhân
- Affina_care_renew
- Affina 100
- Bảo hiểm y tế vượt trội
- Tận Tâm
- Y Tế Vượt Trội
- Bảo hiểm du lịch Pacific Cross
- Master_new
- Master_renew
- VBI Care nhỏ hơn 7 tuổi
- VBI Care nhỏ từ 7 đến 50
- VBI Care trên 50
- Bảo hiểm 37 bệnh/Tình trạng hiểm nghèo
- Chăm Sóc Học Sinh
- Chăm Sóc Sinh Viên
- Chăm Sóc Sinh Viên Sinh Viên
- BVAG
- BVTB_new
- BVTB_renew
- BV_Intercare
- Bệnh hiểm nghèo
- Medical Care
- Bảo Hiểm Ung Thư
- Bảo hiểm bệnh hiểm nghèo
- Bảo hiểm tai nạn nhóm
- Sức Khoẻ Toàn Diện
- SKTA
- SKTA_new
- Tai nạn 24/7
- MIC Care
- Affina_care
- Affina_care_new
- Phúc An Sinh

Bảo hiểm xe máy:
- Bảo hiểm Lái xe, người ngồi trên xe máy
- Bảo hiểm Trách nhiệm Dân sự xe máy

Bảo hiểm y tế xã hội:
- BHXH 1 THÁNG_NEW
- BHXH 1 THÁNG_RENEW
- BHXH 3 THÁNG_NEW
- BHXH 3 THÁNG_RENEW
- BHXH 6 THÁNG_NEW
- BHXH 6 THÁNG_RENEW
- BHXH 12 THÁNG_NEW
- BHXH 12 THÁNG_RENEW
- BHYTHGD 3 THÁNG_NEW
- BHYTHGD 3 THÁNG_RENEW
- BHYTHGD 6 THÁNG_NEW
- BHYTHGD 6 THÁNG_RENEW
- BHYTHGD 12 THÁNG_NEW
- BHYTHGD 12 THÁNG_RENEW
