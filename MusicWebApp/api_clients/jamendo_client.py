# MusicWebApp/api_clients/jamendo_client.py
import requests
import json
import time # Để thêm độ trễ giữa các request (tuân thủ rate limit)

# ==============================================================================
# THAY THẾ BẰNG CLIENT ID THỰC TẾ CỦA BẠN SAU KHI ĐĂNG KÝ VỚI JAMENDO
# ==============================================================================
JAMENDO_CLIENT_ID = 'f66d7dd9'
# ==============================================================================

JAMENDO_API_BASE_URL = 'https://api.jamendo.com/v3.0'

def search_tracks(query, limit=10, offset=0, order='popularity_month', imagesize=200):
    """
    Tìm kiếm bài hát trên Jamendo API và trích xuất thông tin cần thiết.

    Args:
        query (str): Từ khóa tìm kiếm (ví dụ: tên bài hát, nghệ sĩ, thể loại).
        limit (int): Số lượng kết quả tối đa trả về. Tối đa theo tài liệu là 200.
        offset (int): Vị trí bắt đầu lấy kết quả (cho phân trang).
        order (str): Tiêu chí sắp xếp kết quả (ví dụ: 'popularity_month', 'releasedate_desc').
        imagesize (int): Kích thước ảnh bìa mong muốn (ví dụ: 50, 100, 200, 300, 600).

    Returns:
        list: Danh sách các dictionary, mỗi dictionary chứa thông tin chi tiết của một bài hát.
              Trả về danh sách rỗng nếu có lỗi hoặc không tìm thấy kết quả.
    """
    if not JAMENDO_CLIENT_ID or JAMENDO_CLIENT_ID == 'YOUR_ACTUAL_JAMENDO_CLIENT_ID':
        print("LỖI: Vui lòng cung cấp JAMENDO_CLIENT_ID hợp lệ trong file api_clients/jamendo_client.py")
        print("Bạn cần đăng ký ứng dụng tại https://devportal.jamendo.com/ để nhận Client ID.")
        return []

    endpoint = f"{JAMENDO_API_BASE_URL}/tracks/"
    params = {
        'client_id': JAMENDO_CLIENT_ID,
        'format': 'json', # Yêu cầu định dạng JSON
        'limit': limit,
        'offset': offset,
        'search': query,
        'order': order,
        'imagesize': imagesize,
        'include': 'musicinfo' # Yêu cầu thêm thông tin trong musicinfo (chứa tags/genres)
    }

    request_timeout_seconds = 15

    print(f"Đang gửi request đến Jamendo API: {endpoint}")
    print(f"Với các tham số: {params}")

    try:
        response = requests.get(endpoint, params=params, timeout=request_timeout_seconds) # Tăng timeout lên 15 giây
        response.raise_for_status()  # Ném lỗi nếu mã trạng thái HTTP là 4xx hoặc 5xx

        data = response.json() # Parse JSON response

        # Kiểm tra cấu trúc header của Jamendo API response
        if 'headers' in data and data['headers']['status'] == 'success':
            if 'results' in data and data['results']:
                parsed_tracks_info = []
                for track_data in data['results']:
                    # Trích xuất thông tin dựa trên cấu trúc JSON của Jamendo
                    # Luôn kiểm tra tài liệu API mới nhất vì cấu trúc có thể thay đổi

                    # Lấy genre từ musicinfo.tags.genres (nếu có)
                    # Tài liệu bạn cung cấp ghi là musicinfo -> tags (danh sách các tag)
                    # Thử lấy genre từ đó
                    genre_list = track_data.get('musicinfo', {}).get('tags', {}).get('genres', [])
                    main_genre = genre_list[0] if genre_list else None # Lấy genre đầu tiên

                    # Lấy các tag khác (nếu có)
                    other_tags = track_data.get('musicinfo', {}).get('tags', {}).get('vartags', [])


                    track_info = {
                        'jamendo_id': track_data.get('id'), # ID của bài hát trên Jamendo
                        'title': track_data.get('name'),
                        'artist_name': track_data.get('artist_name'),
                        'album_name': track_data.get('album_name'),
                        # API có thể trả về 'image' hoặc 'album_image'. Ưu tiên 'album_image'.
                        'image_url': track_data.get('album_image') or track_data.get('image'),
                        'stream_url': track_data.get('audio'), # Link stream MP3 (thường là 96kbps)
                        'download_url': track_data.get('audiodownload'), # Link tải (nếu audiodownload_allowed là true)
                        'audiodownload_allowed': track_data.get('audiodownload_allowed', False),
                        'source_url': track_data.get('shareurl'), # Link đến trang bài hát trên Jamendo
                        'duration': track_data.get('duration'), # Thời lượng tính bằng giây
                        'genre': main_genre, # Genre chính
                        'tags': other_tags, # Danh sách các tag khác
                        'releasedate': track_data.get('releasedate')
                    }
                    parsed_tracks_info.append(track_info)
                return parsed_tracks_info
            else:
                print("  API trả về thành công nhưng không có kết quả (results) nào.")
                return [] # Không có bài hát nào trong results
        else:
            error_message = "Không rõ lỗi"
            if 'headers' in data and 'error_message' in data['headers']:
                error_message = data['headers']['error_message']
            elif 'headers' in data and 'warnings' in data['headers']: # API có thể trả về warnings
                 error_message = str(data['headers']['warnings'])
            print(f"  Jamendo API trả về trạng thái không thành công hoặc lỗi: {error_message}")
            return []

    except requests.exceptions.HTTPError as http_err:
        print(f"Lỗi HTTP khi gọi Jamendo API: {http_err}")
        if hasattr(http_err, 'response') and http_err.response is not None:
            print(f"  Mã trạng thái: {http_err.response.status_code}")
            print(f"  Nội dung lỗi (nếu có): {http_err.response.text}")
    except requests.exceptions.ConnectionError as conn_err:
        print(f"Lỗi kết nối khi gọi Jamendo API: {conn_err}")
    except requests.exceptions.Timeout as timeout_err:
        print(f"Request đến Jamendo API bị timeout (sau {request_timeout_seconds} giây): {timeout_err}")
    except requests.exceptions.RequestException as req_err:
        print(f"Lỗi request không xác định khi gọi Jamendo API: {req_err}")
    except json.JSONDecodeError:
        print(f"Lỗi: Không thể parse JSON response từ Jamendo API. Nội dung response: {response.text if 'response' in locals() else 'Không có response'}")
    except Exception as e:
        print(f"Một lỗi không mong muốn đã xảy ra: {e}")

    return [] # Trả về danh sách rỗng nếu có bất kỳ lỗi nào

# Phần này để bạn có thể chạy file này trực tiếp để kiểm tra
if __name__ == '__main__':
    print("--- Bắt đầu kiểm tra Jamendo API Client ---")

    if JAMENDO_CLIENT_ID == 'YOUR_ACTUAL_JAMENDO_CLIENT_ID':
        print("\n!!! CẢNH BÁO: Bạn CHƯA CUNG CẤP JAMENDO_CLIENT_ID thực tế ở đầu file này. !!!")
        print("!!! Script sẽ không thể gọi API thành công. Hãy thay thế 'YOUR_ACTUAL_JAMENDO_CLIENT_ID'. !!!\n")

    # Ví dụ các từ khóa tìm kiếm
    test_queries = ["relaxing piano", "upbeat electronic", "NonExistentQueryStringForTestingErrors"]

    for query in test_queries:
        print(f"\nĐang tìm kiếm bài hát với từ khóa: '{query}'...")
        # Lấy 3 bài hát cho mỗi từ khóa để kiểm tra
        tracks = search_tracks(query, limit=3, imagesize=100)

        if tracks:
            print(f"  Tìm thấy {len(tracks)} bài hát:")
            for i, track in enumerate(tracks):
                print(f"\n  --- Thông tin Bài hát {i+1} ---")
                for key, value in track.items():
                    # Định dạng lại một chút cho dễ đọc
                    formatted_key = key.replace('_', ' ').capitalize()
                    print(f"    {formatted_key}: {value}")
        else:
            print(f"  Không tìm thấy bài hát nào hoặc có lỗi xảy ra cho từ khóa '{query}'.")

        # Rất quan trọng: Thêm độ trễ giữa các lần gọi API để tuân thủ rate limit của Jamendo
        # Jamendo không công bố rõ rate limit, nhưng 1 giây là một khoảng thời gian an toàn.
        print("\n  Đang chờ 1 giây trước khi gửi request tiếp theo...")
        time.sleep(1)

    print("\n--- Kết thúc kiểm tra Jamendo API Client ---")
