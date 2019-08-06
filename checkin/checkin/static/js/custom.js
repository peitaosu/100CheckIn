!(function () {
    let view = document.getElementById('view');
    let preview = document.getElementById('preview');
    let full = document.getElementById('full');
    let canvas = document.getElementById('canvas');
    let take = document.getElementById('take');
    let photo = document.getElementById('photo');
    let source = document.getElementById('source');
    source.onchange = getStream;
    let videoPlaying = false;
    let photoCaptured = false;
    let angle = 0;

    navigator.mediaDevices.enumerateDevices()
        .then(gotDevices).then(getStream)

    function gotDevices(deviceInfos) {
        for (var i = 0; i !== deviceInfos.length; ++i) {
            var deviceInfo = deviceInfos[i];
            var option = document.createElement('option');
            option.value = deviceInfo.deviceId;
            if (deviceInfo.kind === 'videoinput') {
                option.text = deviceInfo.label || 'camera ' +
                    (source.length + 1);
                source.appendChild(option);
            }
        }
    }

    function getStream() {
        if (window.stream) {
            window.stream.getTracks().forEach(function (track) {
                track.stop();
            });
        }

        var constraints = {
            audio: false,
            video: {
                deviceId: { exact: source.value },
                width: { ideal: 4096 },
                height: { ideal: 4096 }
            }
        };

        navigator.mediaDevices.getUserMedia(constraints).
            then(gotStream);
    }

    function gotStream(stream) {
        window.stream = stream;
        preview.srcObject = stream;
        preview.onloadedmetadata = function (e) {
            preview.play();
            videoPlaying = true;
        };
        full.srcObject = stream;
        full.onloadedmetadata = function (e) {
            full.play();
        };
    }

    take.addEventListener('click', function () {
        if (videoPlaying) {
            canvas.width = full.videoWidth;
            canvas.height = full.videoHeight;
            canvas.getContext('2d').drawImage(full, 0, 0);
            let data = canvas.toDataURL('image/png');
            photo.setAttribute('src', data);
            photoCaptured = true;
        }
    }, false);

})();
