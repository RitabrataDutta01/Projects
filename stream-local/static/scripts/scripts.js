const audio = document.getElementById("audioPlayer");
const nowPlaying = document.getElementById("now-playing");
const playPauseBtn = document.getElementById("playPauseBtn");
const progressBar = document.getElementById("progressBar");
const currentTimeElem = document.getElementById("currentTime");
const durationElem = document.getElementById("duration");
const sidebar = document.getElementById("sidebar");
const menuToggle = document.getElementById("menuToggle");

let songs = [];
let currentIndex = -1;

document.addEventListener("DOMContentLoaded", () => {
    songs = Array.from(document.querySelectorAll(".song")).map(s => s.querySelector('.song-title').innerText.trim());

    // Mobile Menu Toggle logic
    menuToggle.onclick = () => {
        sidebar.classList.toggle("active");
    };
});

function playSong(songName) {
    audio.src = `/stream/${encodeURIComponent(songName)}`;
    audio.play();
    nowPlaying.innerText = songName;
    currentIndex = songs.indexOf(songName);
    playPauseBtn.innerHTML = '<i class="fas fa-pause"></i>';

    // Highlight active
    document.querySelectorAll('.song').forEach(s => s.classList.remove('playing'));
    const allSongDivs = document.querySelectorAll('.song');
    if (currentIndex > -1) allSongDivs[currentIndex].classList.add('playing');

    // Close sidebar on mobile after selection
    if (window.innerWidth <= 768) {
        sidebar.classList.remove("active");
    }
}

function togglePlay() {
    if (audio.paused) {
        audio.play();
        playPauseBtn.innerHTML = '<i class="fas fa-pause"></i>';
    } else {
        audio.pause();
        playPauseBtn.innerHTML = '<i class="fas fa-play"></i>';
    }
}

function nextSong() {
    if (songs.length === 0) return;
    currentIndex = (currentIndex + 1) % songs.length;
    playSong(songs[currentIndex]);
}

function prevSong() {
    if (songs.length === 0) return;
    currentIndex = (currentIndex - 1 + songs.length) % songs.length;
    playSong(songs[currentIndex]);
}

audio.ontimeupdate = () => {
    const percent = (audio.currentTime / audio.duration) * 100;
    progressBar.value = percent || 0;
    currentTimeElem.innerText = formatTime(audio.currentTime);
    durationElem.innerText = formatTime(audio.duration);
};

audio.onended = () => {
    nextSong();
};

progressBar.oninput = () => {
    audio.currentTime = (progressBar.value / 100) * audio.duration;
};

function formatTime(s) {
    if (isNaN(s)) return "0:00";
    const min = Math.floor(s / 60);
    const sec = Math.floor(s % 60);
    return `${min}:${sec < 10 ? "0" : ""}${sec}`;
}