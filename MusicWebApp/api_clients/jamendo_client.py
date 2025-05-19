import requests
import json
import time

JAMENDO_CLIENT_ID = 'f66d7dd9'
JAMENDO_API_BASE_URL = 'https://api.jamendo.com/v3.0'

def search_tracks(query, limit=10, offset=0, order='popularity_month', imagesize=200):
    if not JAMENDO_CLIENT_ID or JAMENDO_CLIENT_ID == 'YOUR_ACTUAL_JAMENDO_CLIENT_ID':
        print("LỖI: Vui lòng cung cấp JAMENDO_CLIENT_ID hợp lệ trong file api_clients/jamendo_client.py")
        print("Bạn cần đăng ký ứng dụng tại https://devportal.jamendo.com/ để nhận Client ID.")
        return []

    endpoint = f"{JAMENDO_API_BASE_URL}/tracks/"
    params = {
        'client_id': JAMENDO_CLIENT_ID,
        'format': 'json',
        'limit': limit,
        'offset': offset,
        'search': query,
        'order': order,
        'imagesize': imagesize,
        'include': 'musicinfo'
    }

    request_timeout_seconds = 15

    print(f"Đang gửi request đến Jamendo API: {endpoint}")
    print(f"Với các tham số: {params}")

    try:
        response = requests.get(endpoint, params=params, timeout=request_timeout_seconds)
        response.raise_for_status()
        data = response.json()

        if 'headers' in data and data['headers']['status'] == 'success':
            if 'results' in data and data['results']:
                parsed_tracks_info = []
                for track_data in data['results']:
                    genre_list = track_data.get('musicinfo', {}).get('tags', {}).get('genres', [])
                    main_genre = genre_list[0] if genre_list else None
                    other_tags = track_data.get('musicinfo', {}).get('tags', {}).get('vartags', [])

                    track_info = {
                        'jamendo_id': track_data.get('id'),
                        'title': track_data.get('name'),
                        'artist_name': track_data.get('artist_name'),
                        'album_name': track_data.get('album_name'),
                        'image_url': track_data.get('album_image') or track_data.get('image'),
                        'stream_url': track_data.get('audio'),
                        'download_url': track_data.get('audiodownload'),
                        'audiodownload_allowed': track_data.get('audiodownload_allowed', False),
                        'source_url': track_data.get('shareurl'),
                        'duration': track_data.get('duration'),
                        'genre': main_genre,
                        'tags': other_tags,
                        'releasedate': track_data.get('releasedate')
                    }
                    parsed_tracks_info.append(track_info)
                return parsed_tracks_info
            else:
                print("  API trả về thành công nhưng không có kết quả (results) nào.")
                return []
        else:
            error_message = "Không rõ lỗi"
            if 'headers' in data and 'error_message' in data['headers']:
                error_message = data['headers']['error_message']
            elif 'headers' in data and 'warnings' in data['headers']:
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

    return []

if __name__ == '__main__':
    print("--- Bắt đầu kiểm tra Jamendo API Client ---")

    if JAMENDO_CLIENT_ID == 'YOUR_ACTUAL_JAMENDO_CLIENT_ID':
        print("\n!!! CẢNH BÁO: Bạn CHƯA CUNG CẤP JAMENDO_CLIENT_ID thực tế ở đầu file này. !!!")
        print("!!! Script sẽ không thể gọi API thành công. Hãy thay thế 'YOUR_ACTUAL_JAMENDO_CLIENT_ID'. !!!\n")

    test_queries = ["relaxing piano", "upbeat electronic", "NonExistentQueryStringForTestingErrors"]

    for query in test_queries:
        print(f"\nĐang tìm kiếm bài hát với từ khóa: '{query}'...")
        tracks = search_tracks(query, limit=3, imagesize=100)

        if tracks:
            print(f"  Tìm thấy {len(tracks)} bài hát:")
            for i, track in enumerate(tracks):
                print(f"\n  --- Thông tin Bài hát {i+1} ---")
                for key, value in track.items():
                    formatted_key = key.replace('_', ' ').capitalize()
                    print(f"    {formatted_key}: {value}")
        else:
            print(f"  Không tìm thấy bài hát nào hoặc có lỗi xảy ra cho từ khóa '{query}'.")

        print("\n  Đang chờ 1 giây trước khi gửi request tiếp theo...")
        time.sleep(1)

    print("\n--- Kết thúc kiểm tra Jamendo API Client ---")
