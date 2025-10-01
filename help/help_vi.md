# Trình tạo gói thẻ Anki - Hướng dẫn sử dụng

Chào mừng bạn sử dụng Trình tạo gói thẻ Anki! Công cụ này được thiết kế để giúp bạn dễ dàng và hiệu quả tạo ra các thẻ học Anki song ngữ chứa âm thanh, ảnh chụp màn hình và văn bản gốc từ video và phụ đề yêu thích của bạn.
Bạn cũng có thể nhanh chóng tạo các thẻ học Anki song ngữ (có âm thanh) từ những từ vựng hoặc câu ví dụ quý giá của mình bằng định dạng CSV.
Mã nguồn dựa trên giấy phép nguồn mở Apache thân thiện với thương mại, địa chỉ mã nguồn tại [https://github.com/AquariusGit/AnkiGenerator](https://github.com/AquariusGit/AnkiGenerator).

## Mục lục
- [Giới thiệu phần mềm](#giới-thiệu-phần-mềm)
- [Tính năng chính](#tính-năng-chính)
- [Yêu cầu hệ thống](#yêu-cầu-hệ-thống)
- [Sử dụng lần đầu](#sử-dụng-lần-đầu)
- [Tổng quan giao diện](#tổng-quan-giao-diện)
- [Các bước sử dụng](#các-bước-sử-dụng)
  - [Bước 1: Tải xuống video/âm thanh và phụ đề](#bước-1-tải-xuống-videoâm-thanh-và-phụ-đề)
  - [Bước 2: Tạo gói thẻ Anki](#bước-2-tạo-gói-thẻ-anki)
  - [Tùy chọn: Tạo từ tệp CSV](#tùy-chọn-tạo-từ-tệp-csv)
- [Thẻ cấu hình](#thẻ-cấu-hình)
- [Câu hỏi thường gặp (FAQ)](#câu-hỏi-thường-gặp-faq)

---

## Giới thiệu phần mềm

Công cụ này là một ứng dụng giao diện đồ họa có thể tải xuống video/âm thanh và phụ đề đa ngôn ngữ từ các trang web video như YouTube, và xử lý chúng thành các tệp `.apkg` có thể nhập vào Anki. Thẻ được tạo có thể chứa văn bản gốc, bản dịch, các đoạn âm thanh tương ứng, ảnh chụp video, thậm chí thêm tự động phiên âm/pinyin/furigana cho nhiều ngôn ngữ như Trung, Nhật, Hàn, làm phong phú đáng kể tài liệu học ngôn ngữ của bạn.

## Tính năng chính
- **Tải video**: Hỗ trợ tải video hoặc âm thanh thuần từ các trang web như YouTube.
- **Tải phụ đề**: Tự động lấy và tải xuống phụ đề chính thức (vì YouTube không cho phép tải phụ đề tự động tạo mà ẩn danh, nếu muốn hỗ trợ tính năng này, vui lòng tham khảo nội dung trong phần FAQ).
- **Thẻ song ngữ**: Tạo thẻ Anki chứa phụ đề hai ngôn ngữ chỉ bằng một cú nhấp chuột.
- **Trích xuất âm thanh**: Tự động trích xuất các đoạn âm thanh tương ứng với từng phụ đề từ video.
- **Chụp ảnh video**: Tự động chụp ảnh cho từng thẻ từ video hoặc từ mạng.
- **Hỗ trợ CSV**: Tạo âm thanh TTS và thẻ Anki từ các tệp định dạng CSV có hai cột.
- **Hỗ trợ TTS**: Khi không có video hoặc âm thanh, có thể sử dụng các công cụ như gTTS hoặc Edge-TTS để tạo âm thanh cho phụ đề.
- **Tự động phiên âm**:
    - Tự động thêm furigana cho Kanji tiếng Nhật.
    - Tự động thêm pinyin cho Hán tự tiếng Trung.
    - Tự động thêm phiên âm La tinh cho tiếng Hàn.
- **Tùy chỉnh cao**:
    - Tùy chỉnh mẫu và kiểu dáng thẻ Anki.
    - Điều chỉnh thời gian phụ đề.
    - Nhiều tùy chọn xử lý sau, như tự động dọn file tạm.
- **Giao diện đa ngôn ngữ**: Hỗ trợ nhiều ngôn ngữ giao diện như tiếng Anh, Trung giản thể/phồn thể, tiếng Nhật, Hàn, Việt Nam và nhiều hơn nữa.

## Yêu cầu hệ thống
- **Python**: Cần cài đặt môi trường Python 3.x.
- **FFmpeg**: Có thể cài đặt **FFmpeg** và thêm vào biến môi trường (PATH) của hệ thống. FFmpeg được dùng để trích xuất âm thanh từ video và chụp ảnh màn hình. Nếu không được cài đặt đúng cách, các tính năng liên quan sẽ không khả dụng. Nếu xác nhận không cài đặt FFmpeg, vui lòng không chọn âm thanh `gốc` khi sử dụng.

## Sử dụng lần đầu
Khi bạn lần đầu chạy phần mềm này, mặc định sẽ sử dụng ngôn ngữ hệ thống hiện tại. Nếu ngôn ngữ hệ thống hiện tại không được hỗ trợ, nó sẽ chuyển sang tiếng Anh.

## Tổng quan giao diện
Giao diện chính của phần mềm gồm ba phần chính:
 
1.**Bên trái - Thẻ chức năng**:

- **Tải video/âm thanh và phụ đề**: Tải nguyên liệu từ Youtube.
- **Tạo gói Anki bằng phụ đề**: Sử dụng nguyên liệu cục bộ hoặc đã tải để tạo thẻ.
- **Tạo thẻ bằng CSV**: Tạo thẻ hàng loạt từ một tệp `.csv`.
- **Cấu hình**: Thiết lập hành vi mặc định và mẫu Anki cho phần mềm.

2.**Bên phải - Cửa sổ nhật ký**: Hiển thị tất cả thông tin, cảnh báo và lỗi trong quá trình chạy phần mềm.

3.**Phía dưới - Thanh tiến độ**: Hiển thị tiến độ tải xuống hoặc tạo.

## Các bước sử dụng

### Bước 1: Tải video/âm thanh và phụ đề
Thẻ này được dùng để lấy nguyên liệu cần thiết để làm thẻ từ video trực tuyến. Tuy nhiên, xin lưu ý rằng video hoặc âm thanh tốt nhất nên chỉ chứa một ngôn ngữ đơn lẻ, ví dụ như thuần tiếng Trung hoặc thuần tiếng Nhật, không nên sử dụng video hoặc âm thanh đồng thời chứa nhiều ngôn ngữ. Ví dụ như video đọc tiếng Trung trước rồi đọc tiếng Nhật sau là không phù hợp.

1.  **URL video**: Vui lòng nhập một liên kết video YouTube, liên kết này thường là video đơn lẻ, không phải danh sách hoặc trang video cá nhân (điều này có thể khiến không tải đúng hoặc tải quá nhiều tập tin). Mặc định chỉ hỗ trợ video Youtube. Nếu muốn sử dụng video từ các trang web khác, vui lòng đánh dấu vào ô kiểm sau ô nhập URL, để không kiểm tra định dạng URL, như vậy có thể tải video/âm thanh và phụ đề từ bất kỳ trang web nào yt-dlp hỗ trợ (kết quả vui lòng tự xác nhận).
2.  **Truy vấn ngôn ngữ**: Nhấn nút này, phần mềm sẽ bắt đầu phân tích URL, lấy tất cả định dạng video/âm thanh và ngôn ngữ phụ đề khả dụng.
3.  **Thư mục tải xuống**: Chọn thư mục bạn muốn lưu file đã tải. Nếu không tồn tại, thường sẽ tự động được tạo.
4.  **Định dạng video/âm thanh**: Chọn một định dạng từ danh sách thả xuống. Khuyến nghị chọn định dạng `mp4` chứa cả âm thanh và video, hoặc định dạng `m4a` chỉ âm thanh.
5.  **Ngôn ngữ phụ đề mặt trước/mặt sau**: Lần lượt chọn ngôn ngữ phụ đề muốn sử dụng cho mặt trước và mặt sau của thẻ. Phần mềm sẽ theo `cấu hình` tự động cố gắng chọn ngôn ngữ mặc định.
6.  **Chỉ tải phụ đề**: Nếu bạn đã có tệp video cục bộ, hoặc không muốn tạo ảnh chụp và âm thanh gốc, bạn có thể tích vào mục này, chỉ tải file phụ đề.
7.  **Bắt đầu tải**: Nhấn để bắt đầu tải. Sau khi hoàn thành, phần mềm sẽ hỏi liệu có muốn tự động điền đường dẫn file đã tải vào thẻ `Tạo gói Anki`. Khuyến nghị chọn `Có`.

### Bước 2: Tạo gói thẻ Anki dựa trên phụ đề
Thẻ này là nơi chứa chức năng lõi, dùng để kết hợp các nguyên liệu như phụ đề và video thành gói thẻ Anki.

1.  **Thiết lập đường dẫn tệp**:
    - **Tệp phương tiện (Tùy chọn)**: Chọn tệp video hoặc âm thanh của bạn. Bắt buộc nếu bạn muốn trích xuất âm thanh và ảnh chụp từ video.
    - **Tệp phụ đề mặt trước/mặt sau**: Chọn các tệp phụ đề hai ngôn ngữ (định dạng `.srt` hoặc `.vtt`).
    - **Thư mục đầu ra**: Chọn vị trí lưu trữ gói Anki (`.apkg`) và các tệp tạm thời (nếu thư mục không tồn tại sẽ tự động được tạo).
    - **Tên gói Anki**: Đặt tên cho gói thẻ Anki của bạn, mặc định giống tên tệp phụ đề mặt trước.

2.  **Tùy chọn chính**:
    - **Tùy chọn ảnh chụp**:
        - `Thêm ảnh chụp`: Khi được chọn, sẽ tạo ảnh chụp cho mỗi thẻ (nguồn do người dùng chỉ định, có thể là ảnh chụp từ video, hoặc hình đầu tiên sau tìm kiếm từ khóa trên các công cụ tìm kiếm như Google/Baidu/Bing). Tùy chọn này không chỉ tạo cực kỳ chậm (có nhiều yêu cầu mạng và khả năng thất bại cao), mà còn khiến gói thẻ Anki tạo ra chiếm không gian rất lớn, vui lòng cân nhắc kỹ trước khi sử dụng tính năng này.
        - `Thời điểm chụp ảnh`: Nếu là ảnh chụp video, chọn chụp vào đầu, giữa hay cuối phụ đề.
        - `Chất lượng`: Chất lượng ảnh chụp, từ 1-31, số càng nhỏ chất lượng càng cao (tệp cũng càng lớn).
    - **Công cụ TTS**: Công cụ dùng để tạo âm thanh khi không có tệp phương tiện hoặc trích xuất âm thanh thất bại. `gTTS` và `edge-tts` đều là lựa chọn tốt, pyttsx3 sử dụng chức năng TTS cục bộ, nhanh nhưng hiệu quả thấp hơn. `Không tạo MP3` sẽ không tạo âm thanh. Với `gTTS` và `edge-tts`, vui lòng tự xác nhận xem có khả dụng không (có thể xác nhận bằng cách truy cập trang web Google). Nếu không chắc chắn, khuyến nghị sử dụng pyttsx3.
    - **Giọng nói chậm**: Khi được chọn, gTTS sẽ tạo âm thanh với tốc độ chậm hơn (các công cụ TTS khác hiện chưa hỗ trợ).
    - **Dọn dẹp phụ đề**: Tích `Xóa... nội dung không phải hội thoại` sẽ tự động xóa nội dung như `[Nhạc]`, `(Vỗ tay)` trong phụ đề.
    - **Tùy chọn phiên âm**: Khi được chọn, sẽ thêm phiên âm cho văn bản Trung/Nhật/Hàn ở mặt trước hoặc mặt sau.
    - **Độ lệch (ms)**: Nếu có độ trễ cố định giữa âm thanh và phụ đề, nhập số mili giây để hiệu chỉnh (số dương làm âm thanh sớm hơn, số âm làm âm thanh trễ hơn).
    - **Khoảng thời gian phụ đề**: Nếu bạn chỉ muốn tạo thẻ cho một phần nào đó của video, hãy nhập thời gian bắt đầu và kết thúc tại đây (định dạng `HH:MM:SS`).
    - **Dọn dẹp**: Sau khi gói Anki được tạo thành công, các tệp trung gian được tạo trong quá trình sẽ được tự động xóa, bao gồm âm thanh tạm, ảnh chụp và tệp dữ liệu.
    - **Ghi đè mục tiêu**: Khi được chọn, nếu đã tồn tại tệp cùng tên trong thư mục đầu ra, sẽ trực tiếp ghi đè.

3.  **Tạo và xem trước**:
    - **Xem trước**: Tạo nhanh một tệp HTML mà không tạo gói hoàn chỉnh, để xem trước hiệu ứng trong trình duyệt. Bản xem trước không chứa âm thanh và hình ảnh xem trước, chỉ chứa văn bản (và phiên âm).
    - **Tạo**: Nhấn để bắt đầu quá trình tạo gói thẻ Anki cuối cùng.

### Tùy chọn: Tạo từ tệp CSV
Nếu bạn đã có văn bản đối chiếu song ngữ được tổ chức sẵn, bạn có thể sử dụng tính năng này để nhanh chóng làm thẻ.

1.  **Chuẩn bị tệp CSV**: Tạo một tệp `.csv`, **cột đầu tiên** là văn bản mặt trước của thẻ, **cột thứ hai** là văn bản mặt sau của thẻ. Bắt buộc sử dụng mã hóa `UTF-8`. Nếu cần tts tạo âm thanh, vui lòng không thêm nội dung phiên âm.
2.  **Tệp CSV**: Trong phần mềm, chọn tệp CSV đã chuẩn bị của bạn.
3.  **Tùy chọn cài đặt**: Tương tự thẻ "Tạo gói Anki", bạn có thể cài đặt thư mục đầu ra, tên gói, công cụ TTS và tùy chọn phiên âm. Vui lòng đảm bảo ngôn ngữ mặt trước và mặt sau đã chọn phù hợp với tệp CSV, nếu không phát âm sẽ không chính xác.
4.  **Tạo**: Nhấn nút để bắt đầu tạo gói Anki. Ở chế độ này sẽ không có chức năng trích xuất âm thanh và chụp ảnh, âm thanh sẽ hoàn toàn phụ thuộc vào TTS tạo.

Trước đây khi tôi học ngoại ngữ, tôi sẽ thu thập nhiều câu ví dụ để nhớ dễ dàng. Nhưng với sự phát triển của AI, sẽ tiện lợi hơn nhiều. Ví dụ như có thể để các trợ lý AI như Gemini, ChatGPT hoặc Kimi tạo ra những câu ví dụ tương ứng để học. Một phương pháp học của tôi là tạo ra nhiều câu ví dụ tiếng mẹ đẻ, sau đó tạo 3 đến 5 câu ví dụ ngoại ngữ có cùng ý nghĩa cho mỗi câu ví dụ tiếng mẹ đẻ, như vậy có thể học nhiều cách biểu đạt, và vì sự liên quan nên giúp ghi nhớ hiệu quả. Ví dụ khi tôi học tiếng Nhật, tôi thích dùng câu nhắc sau, để AI giúp tôi tạo ra tệp CSV tương ứng: `Tạo 10 bộ câu ví dụ tiếng Nhật cấp N3, mỗi bộ bao gồm 1 bản dịch tiếng Trung và 3 cách diễn đạt tiếng Nhật có ý nghĩa tương tự, khi tạo CSV, đặt tiếng Trung vào cột đầu tiên, 3 câu ví dụ tiếng Nhật dùng dấu ngắt dòng để tách, sau đó hợp nhất và đặt vào cột thứ hai, tệp CSV sử dụng " để biểu thị dấu phân cách.`. Câu nhắc trên sẽ tạo ra nội dung tương ứng, lưu dưới dạng tệp csv UTF-8. Nếu sử dụng trong các trợ lý AI như Gemini CLI, có thể thêm một câu sau phần nhắc: `Cuối cùng ghi vào tệp n3.csv, lưu ở định dạng UTF-8.` là có thể trực tiếp nhận được một tệp CSV hoàn hảo.


## Thẻ cấu hình
Tại đây bạn có thể tùy chỉnh hành vi mặc định của phần mềm và giao diện thẻ.

- **Ngôn ngữ**: Thiết lập ngôn ngữ sử dụng cho giao diện hiện tại.
- **Ngôn ngữ phụ đề mặt trước/mặt sau mặc định**: Thiết lập ngôn ngữ thường dùng nhất, phần mềm sẽ ưu tiên dùng chúng làm mặc định khi "tải xuống" và "tạo chức năng thẻ Anki" (có thể tự sửa trên giao diện tương ứng).
- **TTS mặc định**: Loại TTS mặc định sử dụng.
- **Khoảng cách yêu cầu mạng**: `gTTS` và `edge-tts` sẽ gọi trực tuyến các dịch vụ được cung cấp bởi nhà cung cấp tương ứng, các nhà cung cấp dịch vụ này thường yêu cầu ít nhất 0.5s khoảng cách giữa hai lần gọi.
- **Mẫu và kiểu Anki**:
    - **Mẫu mặt trước/mặt sau**: Sử dụng cú pháp mẫu Anki (ví dụ `{{Question}}`, `{{Audio_Answer}}`) để tùy chỉnh bố cục mặt trước và mặt sau của thẻ.
    - **Bảng kiểu dáng**: Sử dụng mã CSS để tùy chỉnh phông chữ, màu sắc, nền và các giao diện khác của thẻ.
- **Mẫu HTML xem trước**: Tùy chỉnh cấu trúc cơ bản của tệp HTML được tạo khi nhấp vào nút "Xem trước". Nói chung không khuyến nghị sửa đổi.
- **Lưu và khôi phục**:
    - `Lưu cấu hình`: Lưu tất cả các thay đổi cài đặt ở trên.
    - `Khôi phục cấu hình`: Hoàn tác thay đổi, khôi phục về trạng thái đã lưu lần trước.


## Câu hỏi thường gặp (FAQ)
1.  **Hỏi: Làm cách nào để cài đặt yt-dlp và FFmpeg**
    Đáp: FFmpeg không bắt buộc, nhưng nếu bạn cần trích xuất nội dung từ video/âm thanh thì cần cài đặt. Tải về từ [trang web chính thức FFmpeg](https://ffmpeg.org/), giải nén, thêm đường dẫn đầy đủ thư mục `bin` vào biến môi trường `PATH` của hệ điều hành, sau đó khởi động lại phần mềm này.

2.  **Hỏi: Tại sao liên kết YouTube tôi dán vào lại được nhắc là không hợp lệ?**
    Đáp: Công cụ này hiện chỉ hỗ trợ URL video đơn, không hỗ trợ URL danh sách phát (Playlist). Vui lòng đảm bảo liên kết của bạn không chứa tham số `list=`. Nếu bạn xác nhận muốn sử dụng video từ trang web khác hoặc dùng phần mềm như một giao diện cho yt-dlp, vui lòng tích vào ô kiểm sau địa chỉ URL để bỏ qua kiểm tra URL.

3.  **Hỏi: Chức năng phiên âm hỗ trợ ngôn ngữ nào?**
    Đáp: Hiện hỗ trợ thêm furigana cho tiếng Nhật, thêm pinyin cho tiếng Trung, thêm phiên âm La tinh cho tiếng Hàn. Phần mềm sẽ tự động xác định theo tên tệp phụ đề bạn chọn hoặc ngôn ngữ mặc định trong cấu hình. Vì kiến thức của riêng tôi có giới hạn, nên không rõ còn ngôn ngữ nào khác cần thêm phiên âm. Nếu cần, bạn có thể gửi `issue` trên `github`.

4.  **Hỏi: gTTS và edge-tts cũng như pyttsx3 có gì khác nhau?**
    Đáp: Tất cả đều là công cụ chuyển văn bản thành giọng nói. gTTS (Google Text-to-Speech) có thể chậm hơn một chút nhưng hỗ trợ phát chậm. edge-tts (Microsoft Edge Text-to-Speech) thường có giọng nói tự nhiên hơn, chất lượng cao hơn nhưng không hỗ trợ phát chậm. Bạn có thể chọn theo nhu cầu. pyttsx3 thì là công cụ giọng nói cục bộ, cực nhanh nhưng có thể chỉ hỗ trợ một số ít ngôn ngữ, vì vậy khi gtts và edge-tts khả dụng, ưu tiên dùng hai công cụ này. Nếu một công cụ thất bại, phần mềm sẽ tự động thử công cụ khác.

5.  **Hỏi: Có vấn đề gì khi sử dụng phụ đề tự động tạo của youtube để tạo gói ANKI không**
    Đáp: Vì phụ đề tự động tạo, trong đó việc ngắt câu có thể có nhiều vấn đề, dẫn đến việc âm thanh được tạo và trích xuất có thể gặp sự cố, tôi đã từng thử nhiều video nhưng không phù hợp lắm, nên không khuyến khích sử dụng phụ đề tự động, tốt nhất dùng phụ đề do người tạo cung cấp.

6.  **Hỏi: Tại sao thỉnh thoảng gói anki được tạo lại lỗi khi nhập vào**
    Đáp: Điều này khó xác định. Vì tôi đã gặp phải vấn đề tương tự trên máy tính của mình, đôi khi tạo lại là được hoặc nhập vào điện thoại sẽ chính xác. Nếu bạn có thể tái tạo vấn đề này, có thể gửi tệp phụ đề hoặc tệp csv tương ứng, tôi sẽ cố gắng sửa chữa.

7.  **Hỏi: Làm thế nào để tải phụ đề tự động tạo của youtube**
    Đáp: Đầu tiên cài đặt tiện ích `Get cookies.txt LOCALLY`, sau đó xuất `cookies.txt`, rồi đặt vào thư mục phần mềm, cùng cấp với `config.json`. Khi phần mềm phát hiện sự tồn tại của `cookies.txt`, nó sẽ tự động kích hoạt tải phụ đề tự động tạo của youtube. Lưu ý cookie của Youtube có hiệu lực trong 6 giờ, sau thời gian hết hiệu lực không thể đảm bảo tải phụ đề tự động tạo thành công. Tốt nhất là cập nhật cookies.txt trước khi sử dụng.

8.  **Hỏi: Có tệp CSV mẫu không**
    Đáp: Có bốn tệp csv mẫu trong thư mục `examples`. `cn-ja.csv` là ví dụ mặt trước tiếng Trung, mặt sau tiếng Nhật, `en-cn.csv` là ví dụ mặt trước tiếng Anh, mặt sau tiếng Trung. `cn-ja-multi.csv` là ví dụ mặt trước tiếng Trung, mặt sau có nhiều tiếng Nhật, `en-cn-multi.csv` là ví dụ mặt trước tiếng Anh, mặt sau nhiều tiếng Trung. Có thể dùng bốn tệp này để trải nghiệm chức năng tạo gói thẻ Anki bằng CSV.

9.  **Hỏi: Có thể hỗ trợ phương ngữ được không**
    Đáp: Hiện chưa hỗ trợ, sẽ xem xét sau.

10. **Hỏi: Có thể chỉ định giọng nam/nữ không**
    Đáp: Nếu dùng `edge-tts` mặc định là giọng nam, còn `gtts` thì mặc định là giọng nữ.

11. **Hỏi: Một số ngôn ngữ tạo âm thanh không được**
    Đáp: Vì bản thân tôi chỉ biết ba ngôn ngữ: Trung, Anh và Nhật. Nhiều ngôn ngữ dù được edge-tts và gtts hỗ trợ, nhưng tôi thật sự không thể kiểm tra hỗ trợ tất cả ngôn ngữ, khó tránh khỏi sai sót. Nếu bạn biết lập trình, có thể tìm `_male_lang_to_voice` trong tệp `app/aquarius/service/tts_generator.py`, tự tìm ngôn ngữ tương ứng, kiểm tra xem mô hình giọng nói `edge-tts` tương ứng có đúng không (mặc dù đã kiểm tra, nhưng thực sự chưa trải qua kiểm tra đầy đủ, không thể đảm bảo được). Hoặc gửi `issue` trên `github`.

12. **Hỏi: Tại sao khi truy vấn thông tin video không có định dạng video/âm thanh**
    Đáp: Vì Youtube sẽ thay đổi quy tắc định kỳ, nên đôi khi `yt-dlp` không thể lấy được định dạng video/âm thanh tương ứng một cách chính xác, nên cần cập nhật `yt-dlp` định kỳ. Nếu dùng cách `chạy trực tiếp`, có thể vào thư mục `venv` trong thư mục chính chương trình rồi chạy `update_yt_dlp.bat` (nền tảng Windows) hoặc `update_yt_dlp.sh` (nền tảng Linux/MacOS), sau khi cập nhật `yt-dlp`, khởi động lại phần mềm và thử lại.