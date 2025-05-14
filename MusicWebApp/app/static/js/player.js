// MusicWebApp/app/static/js/player.js
document.addEventListener('DOMContentLoaded', function () {
    // ... (các khai báo biến hiện tại của bạn) ...
    const audioPlayer = document.getElementById('audioPlayer');
    const playerBar = document.getElementById('playerBar');

    const playerAlbumArt = document.getElementById('playerAlbumArt');
    const playerSongTitle = document.getElementById('playerSongTitle');
    const playerSongArtist = document.getElementById('playerSongArtist');

    const playPauseBtn = document.getElementById('playPauseBtn');
    const playIcon = 'fa-play';
    const pauseIcon = 'fa-pause';

    const progressBar = document.getElementById('songProgressBar');
    const currentTimeEl = document.getElementById('currentTimeEl');
    const totalTimeEl = document.getElementById('totalTimeEl');

    const volumeBtn = document.getElementById('volumeBtn');
    const volumeSlider = document.getElementById('volumeSlider');
    const volumeUpIcon = 'fa-volume-up';
    const volumeMuteIcon = 'fa-volume-mute';

    let isPlaying = false;
    let currentVolume = 0.7; // Âm lượng mặc định

    // HÀM MỚI ĐỂ TÔ MÀU THANH RANGE
    function updateRangeFill(sliderElement) {
        if (!sliderElement) return;

        const value = parseFloat(sliderElement.value) || 0;
        const min = parseFloat(sliderElement.min) || 0;
        const max = parseFloat(sliderElement.max) || 100;
        const percentage = ((value - min) / (max - min)) * 100;

        // Lấy màu primary từ CSS variables, hoặc dùng màu mặc định
        const primaryColor = getComputedStyle(document.documentElement).getPropertyValue('--primary-color').trim() || '#8c14fc';
        const trackBackgroundColor = 'rgba(255, 255, 255, 0.2)'; // Màu nền của phần chưa fill

        sliderElement.style.background = `linear-gradient(to right, ${primaryColor} ${percentage}%, ${trackBackgroundColor} ${percentage}%)`;
    }


    function formatTime(seconds) {
        // ... (giữ nguyên hàm formatTime của bạn) ...
        if (isNaN(seconds) || !isFinite(seconds) || seconds === null) {
            return "0:00";
        }
        const minutes = Math.floor(seconds / 60);
        const secs = Math.floor(seconds % 60);
        return `${minutes}:${secs < 10 ? '0' : ''}${secs}`;
    }

    window.handlePlayTrack = function(clickedElement) {
        // ... (giữ nguyên hàm handlePlayTrack của bạn) ...
        const songId = clickedElement.dataset.songId;
        const title = clickedElement.dataset.title;
        const artist = clickedElement.dataset.artist;
        const imageUrl = clickedElement.dataset.image;
        const streamUrl = clickedElement.dataset.stream;

        if (!streamUrl || streamUrl.trim() === '') {
            console.error("Lỗi: Không có URL stream hợp lệ cho bài hát:", title);
            alert("Rất tiếc, không thể phát bài hát này (thiếu link stream hoặc link không hợp lệ).");
            return;
        }

        if (playerBar) playerBar.style.display = 'flex';
        if (playerAlbumArt) playerAlbumArt.src = imageUrl;
        if (playerSongTitle) playerSongTitle.textContent = title;
        if (playerSongArtist) playerSongArtist.textContent = artist;

        if (audioPlayer) {
            audioPlayer.src = streamUrl;
            audioPlayer.load();
            audioPlayer.play()
                .catch(error => {
                    console.error("Lỗi khi cố gắng phát nhạc:", error);
                    alert(`Không thể phát bài hát "${title}". Vui lòng thử lại hoặc kiểm tra link stream.`);
                });
        }
    };

    if (playPauseBtn) {
        playPauseBtn.addEventListener('click', () => {
            if (!audioPlayer.src || audioPlayer.src === window.location.href) {
                alert("Vui lòng chọn một bài hát để phát.");
                return;
            }
            if (isPlaying) {
                audioPlayer.pause();
            } else {
                audioPlayer.play().catch(error => console.error("Lỗi khi play:", error));
            }
        });
    }

    audioPlayer.addEventListener('play', () => {
        isPlaying = true;
        if (playPauseBtn) {
            playPauseBtn.querySelector('i').classList.remove(playIcon);
            playPauseBtn.querySelector('i').classList.add(pauseIcon);
            playPauseBtn.title = "Tạm dừng";
        }
    });

    audioPlayer.addEventListener('pause', () => {
        isPlaying = false;
        if (playPauseBtn) {
            playPauseBtn.querySelector('i').classList.remove(pauseIcon);
            playPauseBtn.querySelector('i').classList.add(playIcon);
            playPauseBtn.title = "Phát";
        }
    });

    audioPlayer.addEventListener('loadedmetadata', () => {
        if (totalTimeEl && audioPlayer.duration && isFinite(audioPlayer.duration)) {
            totalTimeEl.textContent = formatTime(audioPlayer.duration);
        } else if (totalTimeEl) {
            totalTimeEl.textContent = "0:00";
        }

        if (progressBar && audioPlayer.duration && isFinite(audioPlayer.duration)) {
            progressBar.max = audioPlayer.duration;
            progressBar.value = 0; // Reset value khi load metadata
            updateRangeFill(progressBar); // CẬP NHẬT FILL BAN ĐẦU
        } else if (progressBar) {
            progressBar.max = 100;
            progressBar.value = 0;
            updateRangeFill(progressBar);
        }
    });

    audioPlayer.addEventListener('timeupdate', () => {
        if (currentTimeEl && audioPlayer.currentTime && isFinite(audioPlayer.currentTime)) {
            currentTimeEl.textContent = formatTime(audioPlayer.currentTime);
        } else if (currentTimeEl) {
            currentTimeEl.textContent = "0:00";
        }

        if (progressBar && audioPlayer.currentTime && isFinite(audioPlayer.currentTime)) {
            progressBar.value = audioPlayer.currentTime;
            updateRangeFill(progressBar); // CẬP NHẬT FILL KHI PHÁT
        } else if (progressBar) {
            progressBar.value = 0;
            updateRangeFill(progressBar);
        }
    });

    if (progressBar) {
        progressBar.addEventListener('input', () => { // 'input' tốt hơn 'change' vì nó cập nhật liên tục khi kéo
            if (audioPlayer.src && audioPlayer.src !== window.location.href && audioPlayer.readyState >= 2) {
                audioPlayer.currentTime = progressBar.value;
                updateRangeFill(progressBar); // CẬP NHẬT FILL KHI NGƯỜI DÙNG KÉO
            }
        });
    }

    audioPlayer.volume = currentVolume;
    if (volumeSlider) {
        volumeSlider.value = currentVolume * 100;
        updateRangeFill(volumeSlider); // CẬP NHẬT FILL BAN ĐẦU CHO VOLUME
    }

    if (volumeSlider) {
        volumeSlider.addEventListener('input', () => {
            currentVolume = volumeSlider.value / 100;
            audioPlayer.volume = currentVolume;
            audioPlayer.muted = false; // Unmute khi người dùng chủ động kéo volume
            updateRangeFill(volumeSlider); // CẬP NHẬT FILL KHI NGƯỜI DÙNG KÉO VOLUME
            // updateVolumeIcon sẽ được gọi bởi 'volumechange'
        });
    }

    if (volumeBtn) {
        volumeBtn.addEventListener('click', () => {
            audioPlayer.muted = !audioPlayer.muted;
            // updateVolumeIcon sẽ được gọi bởi 'volumechange'
            // Nếu muốn fill của volume slider về 0 khi mute, bạn có thể thêm logic ở đây
            // hoặc trong updateVolumeIcon, nhưng thường thì slider vẫn giữ giá trị cũ
        });
    }

    audioPlayer.addEventListener('volumechange', () => {
        updateVolumeIcon();
        if (volumeSlider) {
            // Nếu không mute, cập nhật fill theo volume hiện tại. Nếu mute, có thể fill 0%
            // Tuy nhiên, giữ fill theo giá trị slider có thể trực quan hơn.
            // Dòng này đảm bảo fill được cập nhật nếu volume thay đổi bởi các yếu tố khác
            volumeSlider.value = audioPlayer.muted ? 0 : audioPlayer.volume * 100; // Cập nhật giá trị slider nếu mute
            updateRangeFill(volumeSlider);
        }
    });

    function updateVolumeIcon() {
        // ... (giữ nguyên hàm updateVolumeIcon của bạn) ...
        if (!volumeBtn) return;
        const icon = volumeBtn.querySelector('i');
        if (audioPlayer.muted || audioPlayer.volume === 0) {
            icon.classList.remove(volumeUpIcon);
            icon.classList.add(volumeMuteIcon);
            volumeBtn.title = "Bật tiếng";
        } else {
            icon.classList.remove(volumeMuteIcon);
            icon.classList.add(volumeUpIcon);
            volumeBtn.title = "Tắt tiếng";
        }
    }
    updateVolumeIcon(); // Gọi lần đầu

    audioPlayer.addEventListener('ended', () => {
        console.log("Bài hát đã kết thúc.");
        if (playPauseBtn) {
            playPauseBtn.querySelector('i').classList.remove(pauseIcon);
            playPauseBtn.querySelector('i').classList.add(playIcon);
            playPauseBtn.title = "Phát";
        }
        isPlaying = false;
        if (progressBar) {
            progressBar.value = 0; // Reset thanh tiến trình về đầu
            updateRangeFill(progressBar); // Cập nhật fill về 0%
        }
        if(currentTimeEl) {
            currentTimeEl.textContent = formatTime(0);
        }
        // (Tùy chọn) Phát bài tiếp theo
    });

    // Gọi updateRangeFill cho cả hai thanh trượt khi trang vừa tải xong
    // để đảm bảo chúng có màu nền đúng ngay từ đầu, phòng trường hợp
    // các giá trị ban đầu không phải là 0.
    updateRangeFill(progressBar);
    updateRangeFill(volumeSlider);
});
