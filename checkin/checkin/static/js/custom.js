!(function () {
    let view = document.getElementById('view');
    let preview = document.getElementById('preview');
    let full = document.getElementById('full');
    let canvas = document.getElementById('canvas');
    let take = document.getElementById('take');
    let retake = document.getElementById('retake');
    let take_div = document.getElementById('take_div');
    let retake_div = document.getElementById('retake_div');
    let photo = document.getElementById('photo');
    let source = document.getElementById('source');
    source.onchange = getStream;
    let videoPlaying = false;
    let photoCaptured = false;
    let angle = 0;

    retake_div.style.visibility = "hidden";

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
            take_div.style.visibility = "hidden";
            retake_div.style.visibility = "visible";
            photoCaptured = true;
        }
    }, false);

    retake.addEventListener('click', function () {
        retake_div.style.visibility = "hidden";
        take_div.style.visibility = "visible";
    }, false);

})();
