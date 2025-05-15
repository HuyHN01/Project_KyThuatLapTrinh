// MusicWebApp/app/static/js/player.js
document.addEventListener('DOMContentLoaded', function () {
    const audioPlayer = document.getElementById('audioPlayer');
    const playerBar = document.getElementById('playerBar');

    const playerAlbumArt = document.getElementById('playerAlbumArt');
    const playerSongTitle = document.getElementById('playerSongTitle');
    const playerSongArtist = document.getElementById('playerSongArtist');

    const playPauseBtn = document.getElementById('playPauseBtn');
    const playIcon = 'fa-play';
    const pauseIcon = 'fa-pause';

    const rewindBtn = document.getElementById('rewindBtn');
    const forwardBtn = document.getElementById('forwardBtn');

    const progressBar = document.getElementById('songProgressBar');
    const currentTimeEl = document.getElementById('currentTimeEl');
    const totalTimeEl = document.getElementById('totalTimeEl');

    const volumeBtn = document.getElementById('volumeBtn');
    const volumeSlider = document.getElementById('volumeSlider');
    const volumeUpIcon = 'fa-volume-up';
    const volumeMuteIcon = 'fa-volume-mute';

    let isPlaying = false;
    // currentVolume sẽ được load từ localStorage hoặc mặc định
    // let currentVolume = 0.7; // Bỏ dòng này

    const PLAYER_STATE_KEY = 'myMusicPlayerState';
    let lastSaveTime = 0;
    const SAVE_INTERVAL = 2000; // Lưu trạng thái mỗi 2 giây khi đang phát

    // --- HÀM LƯU TRẠNG THÁI PLAYER ---
    function savePlayerState() {
        if (!audioPlayer) return;

        const state = {
            song: {
                id: playerSongTitle.dataset.songId || null, // Lưu songId nếu có
                title: playerSongTitle.textContent,
                artist: playerSongArtist.textContent,
                imageUrl: playerAlbumArt.src,
                streamUrl: audioPlayer.src
            },
            currentTime: audioPlayer.currentTime,
            duration: audioPlayer.duration,
            isPlaying: isPlaying,
            volume: audioPlayer.volume,
            muted: audioPlayer.muted,
            playerVisible: playerBar.style.display === 'flex'
        };
        localStorage.setItem(PLAYER_STATE_KEY, JSON.stringify(state));
        lastSaveTime = Date.now();
        // console.log('Player state saved:', state);
    }

    // --- HÀM TẢI TRẠNG THÁI PLAYER ---
    function loadPlayerState() {
        const savedStateJSON = localStorage.getItem(PLAYER_STATE_KEY);
        if (!savedStateJSON) {
            // Nếu không có state, đặt âm lượng mặc định và cập nhật fill
            audioPlayer.volume = 0.7;
            if (volumeSlider) {
                volumeSlider.value = 70;
                updateRangeFill(volumeSlider);
            }
            updateVolumeIcon();
            return;
        }

        try {
            const state = JSON.parse(savedStateJSON);
            // console.log('Player state loaded:', state);

            if (state.playerVisible && state.song && state.song.streamUrl && state.song.streamUrl !== window.location.href) {
                if (playerBar) playerBar.style.display = 'flex';

                if (playerAlbumArt) playerAlbumArt.src = state.song.imageUrl || '{{ url_for("static", filename="images/placeholder_cover_small.png") }}';
                if (playerSongTitle) {
                    playerSongTitle.textContent = state.song.title || "Chọn một bài hát";
                    playerSongTitle.dataset.songId = state.song.id; // Khôi phục songId
                }
                if (playerSongArtist) playerSongArtist.textContent = state.song.artist || "Nghệ sĩ";

                if (audioPlayer) {
                    audioPlayer.src = state.song.streamUrl;
                    // Quan trọng: Chỉ set currentTime SAU KHI 'loadedmetadata'
                    // Hoặc nếu audio đã sẵn sàng
                    audioPlayer.addEventListener('loadedmetadata', () => {
                        if (isFinite(state.duration)) {
                            totalTimeEl.textContent = formatTime(state.duration);
                            progressBar.max = state.duration;
                        }
                        if (isFinite(state.currentTime) && state.currentTime < state.duration) {
                            audioPlayer.currentTime = state.currentTime;
                            progressBar.value = state.currentTime;
                        } else {
                            audioPlayer.currentTime = 0;
                            progressBar.value = 0;
                        }
                        updateRangeFill(progressBar);

                        // Nếu trước đó đang phát, thì phát tiếp
                        if (state.isPlaying) {
                            audioPlayer.play().catch(e => console.error("Error playing on load:", e));
                        }
                    }, { once: true }); // { once: true } để listener chỉ chạy 1 lần

                    audioPlayer.volume = state.volume;
                    audioPlayer.muted = state.muted;

                    if (volumeSlider) {
                        volumeSlider.value = state.muted ? 0 : state.volume * 100;
                        updateRangeFill(volumeSlider);
                    }
                    updateVolumeIcon();

                    // isPlaying sẽ được set trong event 'play' hoặc 'pause' của audioPlayer
                    // Hoặc ta có thể set trực tiếp và cập nhật icon nếu không play ngay
                    if (!state.isPlaying) {
                        isPlaying = false;
                        if (playPauseBtn) {
                            playPauseBtn.querySelector('i').classList.remove(pauseIcon);
                            playPauseBtn.querySelector('i').classList.add(playIcon);
                            playPauseBtn.title = "Phát";
                        }
                    }
                     // Nếu duration đã có và hợp lệ thì hiển thị ngay
                    if (totalTimeEl && state.duration && isFinite(state.duration)) {
                        totalTimeEl.textContent = formatTime(state.duration);
                    }
                    if (progressBar && state.duration && isFinite(state.duration)) {
                        progressBar.max = state.duration;
                    }
                    // Cập nhật currentTime và progress bar nếu audio đã có sẵn src (trường hợp F5 nhanh)
                    if (audioPlayer.readyState > 0 && isFinite(state.currentTime) && state.currentTime < (state.duration || Infinity)) {
                         audioPlayer.currentTime = state.currentTime;
                         progressBar.value = state.currentTime;
                         currentTimeEl.textContent = formatTime(state.currentTime);
                         updateRangeFill(progressBar);
                    }


                }
            } else {
                // Nếu không có bài hát hợp lệ hoặc player không visible, đặt âm lượng mặc định
                audioPlayer.volume = state.volume !== undefined ? state.volume : 0.7;
                if (volumeSlider) {
                    volumeSlider.value = (state.volume !== undefined ? state.volume : 0.7) * 100;
                    updateRangeFill(volumeSlider);
                }
                updateVolumeIcon();
            }
        } catch (error) {
            console.error("Lỗi khi tải trạng thái player:", error);
            localStorage.removeItem(PLAYER_STATE_KEY); // Xóa state hỏng
             // Đặt âm lượng mặc định nếu có lỗi
            audioPlayer.volume = 0.7;
            if (volumeSlider) {
                volumeSlider.value = 70;
                updateRangeFill(volumeSlider);
            }
            updateVolumeIcon();
        }
    }

    function updateRangeFill(sliderElement) {
        if (!sliderElement) return;
        const value = parseFloat(sliderElement.value) || 0;
        const min = parseFloat(sliderElement.min) || 0;
        const max = parseFloat(sliderElement.max) || 100;
        const percentage = ((value - min) / (max - min)) * 100;
        const primaryColor = getComputedStyle(document.documentElement).getPropertyValue('--primary-color').trim() || '#8c14fc';
        const trackBackgroundColor = 'rgba(255, 255, 255, 0.2)';
        sliderElement.style.background = `linear-gradient(to right, ${primaryColor} ${percentage}%, ${trackBackgroundColor} ${percentage}%)`;
    }

    function formatTime(seconds) {
        if (isNaN(seconds) || !isFinite(seconds) || seconds === null) {
            return "0:00";
        }
        const minutes = Math.floor(seconds / 60);
        const secs = Math.floor(seconds % 60);
        return `${minutes}:${secs < 10 ? '0' : ''}${secs}`;
    }

    window.handlePlayTrack = function(clickedElement) {
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
        if (playerSongTitle) {
            playerSongTitle.textContent = title;
            playerSongTitle.dataset.songId = songId; // Lưu songId vào data attribute
        }
        if (playerSongArtist) playerSongArtist.textContent = artist;


        if (audioPlayer) {
            audioPlayer.src = streamUrl;
            audioPlayer.load(); // Cần load để lấy metadata
            audioPlayer.play()
                .then(() => {
                    // isPlaying sẽ được set trong event 'play'
                    // Save state sau khi play thành công
                    // savePlayerState(); // Sẽ được save trong 'play' event listener
                })
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
            // savePlayerState(); // Sẽ được save trong 'play'/'pause' event listener
        });
    }

    if (rewindBtn) {
        rewindBtn.addEventListener('click', () => {
            if (audioPlayer.src && audioPlayer.readyState >= 2) {
                const newTime = audioPlayer.currentTime - 10;
                audioPlayer.currentTime = Math.max(0, newTime);
                if (progressBar) updateRangeFill(progressBar); // Cập nhật fill ngay
                savePlayerState(); // Lưu khi tua
            } else { /* ... */ }
        });
    }

    if (forwardBtn) {
        forwardBtn.addEventListener('click', () => {
            if (audioPlayer.src && audioPlayer.readyState >= 2 && isFinite(audioPlayer.duration)) {
                const newTime = audioPlayer.currentTime + 10;
                audioPlayer.currentTime = Math.min(newTime, audioPlayer.duration);
                if (progressBar) updateRangeFill(progressBar); // Cập nhật fill ngay
                savePlayerState(); // Lưu khi tua
            } else { /* ... */ }
        });
    }

    audioPlayer.addEventListener('play', () => {
        isPlaying = true;
        if (playPauseBtn) { /* ... update icon ... */
            playPauseBtn.querySelector('i').classList.remove(playIcon);
            playPauseBtn.querySelector('i').classList.add(pauseIcon);
            playPauseBtn.title = "Tạm dừng";
        }
        savePlayerState(); // Quan trọng: lưu khi bắt đầu phát
    });

    audioPlayer.addEventListener('pause', () => {
        isPlaying = false;
        if (playPauseBtn) { /* ... update icon ... */
            playPauseBtn.querySelector('i').classList.remove(pauseIcon);
            playPauseBtn.querySelector('i').classList.add(playIcon);
            playPauseBtn.title = "Phát";
        }
        savePlayerState(); // Quan trọng: lưu khi tạm dừng
    });

    audioPlayer.addEventListener('loadedmetadata', () => {
        // Phần này đã được xử lý trong loadPlayerState,
        // nhưng vẫn giữ lại để cập nhật UI khi một bài mới được load bình thường (không phải từ localStorage)
        if (totalTimeEl && audioPlayer.duration && isFinite(audioPlayer.duration)) {
            totalTimeEl.textContent = formatTime(audioPlayer.duration);
        } else if (totalTimeEl) {
            totalTimeEl.textContent = "0:00";
        }

        if (progressBar && audioPlayer.duration && isFinite(audioPlayer.duration)) {
            progressBar.max = audioPlayer.duration;
        } else if (progressBar) {
            progressBar.max = 100;
        }
        // Không reset progressBar.value ở đây nữa nếu đang load từ state
        // Nếu là bài hát mới hoàn toàn, currentTime sẽ là 0
        progressBar.value = audioPlayer.currentTime || 0;
        updateRangeFill(progressBar);
        savePlayerState(); // Lưu state khi metadata đã load (có duration)
    });

    audioPlayer.addEventListener('timeupdate', () => {
        if (currentTimeEl && audioPlayer.currentTime && isFinite(audioPlayer.currentTime)) {
            currentTimeEl.textContent = formatTime(audioPlayer.currentTime);
        }

        if (progressBar && audioPlayer.currentTime && isFinite(audioPlayer.currentTime)) {
            progressBar.value = audioPlayer.currentTime;
            updateRangeFill(progressBar);
        }
        // Lưu trạng thái định kỳ khi đang phát
        if (isPlaying && Date.now() - lastSaveTime > SAVE_INTERVAL) {
            savePlayerState();
        }
    });

    if (progressBar) {
        progressBar.addEventListener('input', () => {
            if (audioPlayer.src && audioPlayer.src !== window.location.href && audioPlayer.readyState >= 2) {
                audioPlayer.currentTime = progressBar.value;
                updateRangeFill(progressBar);
                savePlayerState(); // Lưu khi người dùng tua bằng thanh progress
            }
        });
    }

    // audioPlayer.volume sẽ được set bởi loadPlayerState
    // if (volumeSlider) {
    //     volumeSlider.value = (audioPlayer.volume || 0.7) * 100;
    //     updateRangeFill(volumeSlider);
    // }

    if (volumeSlider) {
        volumeSlider.addEventListener('input', () => {
            const newVolume = volumeSlider.value / 100;
            audioPlayer.volume = newVolume;
            audioPlayer.muted = false; // Unmute khi người dùng chủ động kéo volume
            updateRangeFill(volumeSlider);
            // updateVolumeIcon() sẽ được gọi bởi 'volumechange'
            // savePlayerState(); // Sẽ được lưu trong 'volumechange'
        });
    }

    if (volumeBtn) {
        volumeBtn.addEventListener('click', () => {
            audioPlayer.muted = !audioPlayer.muted;
            // savePlayerState(); // Sẽ được lưu trong 'volumechange'
        });
    }

    audioPlayer.addEventListener('volumechange', () => {
        updateVolumeIcon();
        if (volumeSlider) {
            // Cập nhật slider theo trạng thái thực của audioPlayer
             if (audioPlayer.muted) {
                // Giữ nguyên giá trị slider nhưng fill 0% là một lựa chọn,
                // nhưng trực quan hơn có thể là set value = 0
                // Tạm thời để volumeSlider.value = audioPlayer.volume * 100 khi không mute
            } else {
                volumeSlider.value = audioPlayer.volume * 100;
            }
            updateRangeFill(volumeSlider); // Cập nhật fill dựa trên giá trị mới của slider
        }
        savePlayerState(); // Lưu khi âm lượng hoặc mute thay đổi
    });

    function updateVolumeIcon() {
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
    // updateVolumeIcon(); // Sẽ được gọi trong loadPlayerState

    audioPlayer.addEventListener('ended', () => {
        console.log("Bài hát đã kết thúc.");
        if (playPauseBtn) { /* ... */ }
        isPlaying = false;
        if (progressBar) {
            progressBar.value = 0;
            updateRangeFill(progressBar);
        }
        if(currentTimeEl) {
            currentTimeEl.textContent = formatTime(0);
        }
        audioPlayer.currentTime = 0; // Đặt lại thời gian
        savePlayerState(); // Lưu trạng thái khi bài hát kết thúc
    });

    // --- TẢI TRẠNG THÁI PLAYER KHI DOM LOADED ---
    loadPlayerState();

    // Gọi updateRangeFill cho cả hai thanh trượt để đảm bảo màu nền đúng
    // sau khi loadPlayerState (nếu không có state lưu)
    // đã được xử lý trong loadPlayerState() và các event listeners
    // updateRangeFill(progressBar);
    // updateRangeFill(volumeSlider);
});
