# Trình tạo gói thẻ Anki - Hướng dẫn sử dụng

Chào mừng bạn đến với Trình tạo gói thẻ Anki! Công cụ này được thiết kế để giúp bạn dễ dàng và hiệu quả tạo các thẻ học Anki song ngữ với âm thanh, ảnh chụp màn hình và văn bản gốc từ các video và phụ đề yêu thích của bạn.
Mã nguồn dựa trên giấy phép mã nguồn mở Apache thân thiện với doanh nghiệp, và địa chỉ mã nguồn là https://github.com/AquariusGit/AnkiGenerator.

## Mục lục
- [Giới thiệu phần mềm](#giới-thiệu-phần-mềm)
- [Tính năng chính](#tính-năng-chính)
- [Yêu cầu hệ thống](#yêu-cầu-hệ-thống)
- [Sử dụng lần đầu](#sử-dụng-lần-đầu)
- [Tổng quan giao diện](#tổng-quan-giao-diện)
- [Các bước sử dụng](#các-bước-sử-dụng)
  - [Bước một: Tải xuống âm thanh/video và phụ đề](#bước-một-tải-xuống-âm-thanhvideo-và-phụ-đề)
  - [Bước hai: Tạo gói thẻ Anki](#bước-hai-tạo-gói-thẻ-anki)
  - [Tùy chọn: Tạo từ tệp CSV](#tùy-chọn-tạo-từ-tệp-csv)
- [Tab cấu hình](#tab-cấu-hình)
- [Các câu hỏi thường gặp (FAQ)](#các-câu-hỏi-thường-gặp-faq)

---

## Giới thiệu phần mềm

Công cụ này là một ứng dụng giao diện đồ họa có thể tải xuống video/âm thanh và phụ đề đa ngôn ngữ từ các trang web video như YouTube, và xử lý chúng thành các tệp `.apkg` có thể nhập vào Anki. Các thẻ được tạo có thể bao gồm câu gốc, bản dịch, đoạn âm thanh tương ứng, ảnh chụp màn hình video, và thậm chí tự động thêm pinyin/furigana/romanization cho các ngôn ngữ Trung, Nhật, Hàn, làm phong phú đáng kể tài liệu học ngôn ngữ của bạn.

## Tính năng chính
- **Tải xuống video**: Hỗ trợ tải xuống video hoặc chỉ âm thanh từ các trang web như YouTube.
- **Tải xuống phụ đề**: Tự động tìm nạp và tải xuống phụ đề chính thức và phụ đề tự động tạo.
- **Thẻ song ngữ**: Tạo thẻ Anki chứa phụ đề hai ngôn ngữ chỉ bằng một cú nhấp chuột.
- **Trích xuất âm thanh**: Tự động cắt các đoạn âm thanh tương ứng với mỗi phụ đề từ video.
- **Chụp màn hình video**: Tự động chụp khung hình video cho mỗi thẻ.
- **Hỗ trợ TTS**: Khi không có video hoặc âm thanh, có thể sử dụng gTTS hoặc Edge-TTS để tạo giọng nói cho phụ đề.
- **Tự động thêm chú âm**:
    - Tự động thêm Furigana cho chữ Hán tiếng Nhật.
    - Tự động thêm Pinyin cho chữ Hán tiếng Trung.
    - Tự động thêm Romanization cho tiếng Hàn.
- **Tùy chỉnh cao**:
    - Tùy chỉnh mẫu và kiểu thẻ Anki.
    - Điều chỉnh dòng thời gian phụ đề, hợp nhất các dòng phụ đề.
    - Nhiều tùy chọn xử lý hậu kỳ, chẳng hạn như tự động dọn dẹp các tệp tạm thời.
- **Giao diện đa ngôn ngữ**: Hỗ trợ tiếng Anh, tiếng Trung giản thể/phồn thể, tiếng Nhật, tiếng Hàn, tiếng Việt và các ngôn ngữ giao diện khác.

## Yêu cầu hệ thống
- **Python**: Yêu cầu cài đặt môi trường Python 3.x.
- **FFmpeg**: Phải cài đặt **FFmpeg** và thêm nó vào biến môi trường hệ thống (PATH) của bạn. FFmpeg được sử dụng để trích xuất âm thanh và chụp ảnh màn hình từ video. Nếu không được cài đặt đúng cách, các chức năng liên quan sẽ không khả dụng.

## Sử dụng lần đầu
Khi bạn chạy phần mềm này lần đầu tiên, một cửa sổ "Thiết lập ban đầu" sẽ bật lên.
1. **Chọn ngôn ngữ hiển thị**: Chọn ngôn ngữ bạn muốn giao diện phần mềm hiển thị.
2. **Chọn ngôn ngữ mặt trước/mặt sau mặc định**: Đặt ngôn ngữ nguồn (mặt trước) và ngôn ngữ đích (mặt sau) bạn thường xuyên sử dụng nhất. Điều này sẽ tự động chọn ngôn ngữ cho bạn trong các thao tác tiếp theo, nâng cao hiệu quả.
Sau khi thiết lập xong, nhấp vào "Tiếp tục" để vào giao diện chính.

## Tổng quan giao diện
Giao diện chính của phần mềm được chia thành ba phần chính:
1. **Bên trái - Các tab chức năng**:
    - **Tải xuống âm thanh/video và phụ đề**: Tải xuống tài liệu từ URL mạng.
    - **Tạo gói Anki**: Tạo thẻ bằng cách sử dụng tài liệu cục bộ hoặc đã tải xuống.
    - **Tạo thẻ từ tệp CSV**: Tạo hàng loạt thẻ từ tệp `.csv`.
    - **Cấu hình**: Thiết lập hành vi mặc định của phần mềm và các mẫu Anki.
2. **Bên phải - Cửa sổ nhật ký**: Hiển thị tất cả thông tin, cảnh báo và lỗi trong quá trình hoạt động của phần mềm.
3. **Bên dưới - Thanh tiến trình**: Hiển thị tiến trình tải xuống hoặc tạo.

## Các bước sử dụng

### Bước một: Tải xuống âm thanh/video và phụ đề
Tab này được sử dụng để lấy các tài liệu cần thiết để tạo thẻ từ các video trực tuyến. Tuy nhiên, xin lưu ý rằng tốt nhất là video hoặc âm thanh chỉ chứa một loại ngôn ngữ duy nhất, chẳng hạn như tiếng Trung thuần túy hoặc tiếng Nhật thuần túy. Không sử dụng các video hoặc âm thanh chứa nhiều ngôn ngữ cùng lúc. Ví dụ, một video đọc tiếng Trung trước rồi đọc tiếng Nhật thì không phù hợp lắm. Chúng tôi sẽ xem xét liệu có cần cung cấp chức năng này sau này hay không.

1. **URL video**: Dán một liên kết video YouTube. Phần mềm sẽ tự động phát hiện các liên kết hợp lệ trong khay nhớ tạm và điền vào. Thường là một tệp video đơn lẻ, không phải danh sách phát hoặc trang video cá nhân (điều này sẽ dẫn đến việc tải xuống không chính xác hoặc tải xuống quá nhiều tệp). Theo mặc định, chỉ hỗ trợ video YouTube. Nếu bạn muốn sử dụng video từ các trang web khác, vui lòng chọn hộp kiểm sau trường nhập URL để cho biết không kiểm tra định dạng URL, sau đó bạn có thể tải xuống âm thanh/video và phụ đề từ bất kỳ trang web nào được yt-dlp hỗ trợ (vui lòng tự xác nhận kết quả).
2. **Truy vấn ngôn ngữ**: Nhấp vào nút này, phần mềm sẽ bắt đầu phân tích URL để lấy tất cả các định dạng video/âm thanh và ngôn ngữ phụ đề có sẵn.
3. **Thư mục tải xuống**: Chọn thư mục bạn muốn lưu các tệp đã tải xuống.
4. **Định dạng âm thanh/video**: Chọn một định dạng từ danh sách thả xuống. Nên chọn định dạng `mp4` bao gồm cả âm thanh và video, hoặc định dạng `m4a` cho âm thanh thuần túy.
5. **Ngôn ngữ phụ đề mặt trước/mặt sau**: Lần lượt chọn ngôn ngữ phụ đề bạn muốn sử dụng cho mặt trước và mặt sau của thẻ. Phần mềm sẽ tự động cố gắng chọn ngôn ngữ mặc định dựa trên "Cấu hình" của bạn.
6. **Chỉ tải xuống phụ đề**: Nếu bạn đã có tệp video cục bộ, hoặc không muốn tạo ảnh chụp màn hình và âm thanh gốc, bạn có thể chọn tùy chọn này để chỉ tải xuống tệp phụ đề.
7. **Bắt đầu tải xuống**: Nhấp để bắt đầu tải xuống. Sau khi hoàn tất, phần mềm sẽ hỏi bạn có muốn tự động điền đường dẫn tệp đã tải xuống vào tab "Tạo gói Anki" hay không. Nên chọn "Có".

### Bước hai: Tạo gói thẻ Anki
Tab này là nơi chứa chức năng cốt lõi, được sử dụng để kết hợp các tài liệu thành thẻ Anki.

1. **Cài đặt đường dẫn tệp**:
    - **Tệp phương tiện (Tùy chọn)**: Chọn tệp video hoặc âm thanh của bạn. Nếu bạn muốn trích xuất âm thanh và ảnh chụp màn hình từ video, mục này là bắt buộc.
    - **Tệp phụ đề mặt trước/mặt sau**: Chọn tệp phụ đề của hai ngôn ngữ (định dạng `.srt` hoặc `.vtt`).
    - **Thư mục đầu ra**: Chọn vị trí lưu gói Anki (`.apkg`) và các tệp tạm thời được tạo (nếu thư mục không tồn tại, nó sẽ được tạo tự động).
    - **Tên gói Anki**: Đặt tên cho gói thẻ Anki của bạn, mặc định sẽ giống với tên tệp phụ đề mặt trước.

2. **Các tùy chọn chính**:
    - **Tùy chọn chụp màn hình**:
        - `Thêm ảnh chụp màn hình`: Chọn tùy chọn này để tạo ảnh chụp màn hình cho mỗi thẻ.
        - `Thời điểm chụp màn hình`: Chọn chụp màn hình ở đầu, giữa hoặc cuối phụ đề.
        - `Chất lượng`: Chất lượng ảnh chụp màn hình, từ 1-31, số càng nhỏ chất lượng càng cao (và kích thước tệp càng lớn).
    - **Công cụ TTS**: Công cụ nào sẽ được sử dụng để tạo giọng nói khi không có tệp phương tiện hoặc trích xuất âm thanh thất bại. `gTTS` yêu cầu kết nối với dịch vụ của Google, vui lòng tự xác nhận xem có khả dụng hay không. Cả `gTTS` và `edge-tts` đều là những lựa chọn tốt. `Không tạo MP3` sẽ tắt chức năng này. `gTTS` yêu cầu kết nối với dịch vụ của Google, vui lòng tự xác nhận xem có khả dụng hay không.
    - **Giọng nói chậm**: Nếu được chọn, gTTS sẽ tạo giọng nói với tốc độ chậm hơn (edge-tts không hỗ trợ điều này).
    - **Dọn dẹp phụ đề**: Chọn `Xóa... nội dung không phải đối thoại` sẽ tự động xóa các nội dung như `[Nhạc]`, `(Tiếng vỗ tay)` khỏi phụ đề.
    - **Tùy chọn chú âm**: Chọn tùy chọn này để thêm chú âm cho tiếng Trung/Nhật/Hàn ở mặt trước hoặc mặt sau.
    - **Xử lý hậu kỳ**:
        - `Dọn dẹp tệp .mp3/.jpg/.csv`: Nếu được chọn, sau khi gói Anki được tạo thành công, các tệp âm thanh, ảnh chụp màn hình và dữ liệu tạm thời được tạo trong quá trình sẽ tự động bị xóa.
    - **Độ lệch dòng thời gian (ms)**: Nếu có độ trễ cố định giữa âm thanh và phụ đề, hãy nhập số mili giây vào đây để điều chỉnh (số dương làm âm thanh sớm hơn, số âm làm âm thanh trễ hơn).
    - **Khoảng thời gian phụ đề**: Nếu bạn chỉ muốn tạo thẻ cho một phần cụ thể của video, hãy nhập thời gian bắt đầu và kết thúc tại đây (định dạng `HH:MM:SS`).
    - **Hợp nhất phụ đề**:
        - `Hợp nhất các dòng phụ đề có thời gian gần nhau`: Nếu được chọn, các dòng phụ đề ngắn có khoảng thời gian rất gần nhau sẽ được hợp nhất thành một câu, phù hợp để xử lý các video có nhiều đối thoại. Sử dụng chức năng này một cách thận trọng, nó vẫn chưa hoàn thiện, chỉ phù hợp với các phương tiện truyền thông dạng podcast có khoảng thời gian không đều.
        - `Khoảng cách tối đa (ms)`: Xác định khoảng cách gần nhất mà các phụ đề có thể được hợp nhất.
    - **Xử lý tệp**:
        - `Ghi đè gói Anki cùng tên`: Nếu được chọn, nếu một tệp có cùng tên đã tồn tại trong thư mục đầu ra, nó sẽ bị ghi đè trực tiếp.

3. **Tạo và xem trước**:
    - **Xem trước 5 thẻ đầu tiên**: Nhanh chóng tạo một tệp HTML mà không cần tạo toàn bộ gói để xem trước hiệu ứng của 5 thẻ đầu tiên trong trình duyệt. Bản xem trước không bao gồm âm thanh và hình ảnh xem trước.
    - **Tạo gói Anki**: Nhấp để bắt đầu quá trình tạo cuối cùng.

### Tùy chọn: Tạo từ tệp CSV
Nếu bạn đã có văn bản đối chiếu song ngữ được sắp xếp, bạn có thể sử dụng chức năng này để nhanh chóng tạo thẻ.

1. **Chuẩn bị tệp CSV**: Tạo một tệp `.csv`, với **cột đầu tiên** là văn bản mặt trước của thẻ và **cột thứ hai** là văn bản mặt sau của thẻ. Phải được mã hóa UTF-8. Nếu cần TTS để tạo giọng nói, vui lòng không thêm chú âm hoặc các nội dung khác.
2. **Tệp CSV**: Trong phần mềm, chọn tệp CSV bạn đã chuẩn bị.
3. **Tùy chọn cài đặt**: Tương tự như tab "Tạo gói Anki", bạn có thể đặt thư mục đầu ra, tên gói, công cụ TTS và tùy chọn chú âm. Vui lòng đảm bảo rằng ngôn ngữ mặt trước và mặt sau đã chọn nhất quán với tệp CSV, nếu không có thể dẫn đến phát âm không chính xác.
4. **Tạo gói Anki**: Nhấp vào nút để bắt đầu tạo. Trong chế độ này, sẽ không có chức năng trích xuất âm thanh và chụp màn hình, và âm thanh sẽ hoàn toàn được tạo bởi TTS.

## Tab cấu hình
Tại đây, bạn có thể tùy chỉnh hành vi mặc định của phần mềm và giao diện thẻ.

- **Ngôn ngữ phụ đề mặt trước/mặt sau mặc định**: Đặt các ngôn ngữ bạn thường xuyên sử dụng nhất, và phần mềm sẽ ưu tiên chúng trong quá trình "Tải xuống" và "Tự động điền".
- **Mẫu và kiểu Anki**:
    - **Mẫu mặt trước/mặt sau**: Sử dụng cú pháp mẫu của Anki (ví dụ: `{{Question}}`, `{{Audio_Answer}}`) để tùy chỉnh bố cục của mặt trước và mặt sau của thẻ.
    - **Bảng kiểu**: Sử dụng mã CSS để tùy chỉnh phông chữ, màu sắc, nền và các giao diện khác của thẻ.
- **Mẫu HTML xem trước**: Tùy chỉnh cấu trúc cơ bản của tệp HTML được tạo khi nhấp vào nút "Xem trước". Nói chung, không nên sửa đổi điều này.
- **Lưu và khôi phục**:
    - `Lưu cấu hình`: Lưu tất cả các thay đổi của bạn đối với các cài đặt trên.
    - `Khôi phục cấu hình`: Hoàn tác các thay đổi và khôi phục về trạng thái đã lưu cuối cùng.

## Các câu hỏi thường gặp (FAQ)
1. **Hỏi: Phần mềm báo "FFmpeg not found" (Không tìm thấy FFmpeg) thì phải làm sao?**
    Đáp: Bạn cần tải xuống từ trang web chính thức của FFmpeg, giải nén, sau đó thêm đường dẫn đầy đủ của thư mục `bin` của nó vào biến môi trường `PATH` của hệ điều hành của bạn, và sau đó khởi động lại phần mềm này.

2. **Hỏi: Tại sao liên kết YouTube tôi dán lại báo không hợp lệ?**
    Đáp: Công cụ này hiện chỉ hỗ trợ URL video đơn lẻ, không hỗ trợ URL danh sách phát (Playlist). Vui lòng đảm bảo rằng liên kết của bạn không chứa tham số `list=`. Nếu bạn xác nhận muốn sử dụng video từ các trang web khác hoặc sử dụng phần mềm như một giao diện người dùng yt-dlp, thì hãy chọn tùy chọn sau địa chỉ URL để buộc tắt kiểm tra URL.

3. **Hỏi: Chức năng chú âm hỗ trợ những ngôn ngữ nào?**
    Đáp: Hiện tại, nó hỗ trợ thêm Furigana cho tiếng Nhật, Pinyin cho tiếng Trung và Romanization cho tiếng Hàn. Phần mềm sẽ tự động xác định dựa trên tên tệp phụ đề bạn đã chọn hoặc ngôn ngữ mặc định trong cấu hình.

4. **Hỏi: gTTS và edge-tts có gì khác nhau?**
    Đáp: Cả hai đều là công cụ chuyển văn bản thành giọng nói. gTTS (Google Text-to-Speech) có thể chậm hơn một chút nhưng hỗ trợ phát lại chậm. edge-tts (Microsoft Edge Text-to-Speech) thường có giọng nói tự nhiên hơn, chất lượng cao hơn nhưng không hỗ trợ phát lại chậm. Bạn có thể chọn tùy theo nhu cầu của mình. Nếu một công cụ thất bại, phần mềm sẽ tự động thử công cụ khác.

5. **Hỏi: Có vấn đề gì khi sử dụng phụ đề tự động của YouTube để tạo gói ANKI không?**
    Đáp: Điều này khó xác định. Vì phụ đề tự động có thể có nhiều vấn đề về phân đoạn câu, dẫn đến cả giọng nói được tạo và giọng nói được trích xuất đều có thể có vấn đề, vì vậy không nên sử dụng phụ đề tự động; hãy cố gắng sử dụng phụ đề do người tạo cung cấp.