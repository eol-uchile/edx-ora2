export class AudioRecord {

    constructor(){
        this.states = ['Initial', 'Record', 'Download'];
        this.display;
        this.controllerWrapper;
        this.mediaRecorder;
        this.stateIndex = 0;
        this.chunks = [];
        this.audioURL = '';

        // mediaRecorder setup for audio
        if(navigator.mediaDevices && navigator.mediaDevices.getUserMedia){
            console.log('mediaDevices supported..')

            navigator.mediaDevices.getUserMedia({
                audio: true
            }).then(stream => {
                this.mediaRecorder = new MediaRecorder(stream);

                this.mediaRecorder.ondataavailable = (e) => {
                    this.chunks.push(e.data);
                };

                this.mediaRecorder.onstop = () => {
                    const blob = new Blob(this.chunks, {'type': 'audio/ogg; codecs=opus'});
                    this.chunks = [];
                    this.audioURL = window.URL.createObjectURL(blob);
                    document.querySelector('audio').src = this.audioURL;
                    
                };
            }).catch(error => {
                console.log('Following error has occured : ',error);
            });
        } else {
            this.stateIndex = '';
            this.application(this.stateIndex);
        };
    };

    clearDisplay = () => {
        this.display.textContent = ''
    }
    
    clearControls = () => {
        this.controllerWrapper.textContent = ''
    }
    
    record = (event) => {
        event.preventDefault();
        this.stateIndex = 1
        this.mediaRecorder.start()
        this.application(this.stateIndex)
    }
    
    stopRecording = (event) => {
        event.preventDefault();
        this.stateIndex = 2
        this.mediaRecorder.stop()
        this.application(this.stateIndex)
    }
    
    downloadAudio = (event) => {
        event.preventDefault();
        const downloadLink = document.createElement('a')
        downloadLink.href = this.audioURL
        downloadLink.setAttribute('download', 'audio')
        downloadLink.click()
    }
    
    addButton = (id, func, text) => {
        const btn = document.createElement('a')
        btn.id = id
        btn.addEventListener("click", func);
        btn.setAttribute('class', 'audio-record-button')
        btn.textContent = text
        this.controllerWrapper.append(btn)
    }
    
    addMessage = (text) => {
        const msg = document.createElement('p')
        msg.textContent = text
        this.display.append(msg)
    }
    
    addAudio = () => {
        const audio = document.createElement('audio')
        audio.controls = true
        audio.src = this.audioURL
        this.display.append(audio)
    }
    
    application = (index) => {
        switch (this.states[index]) {
            case 'Initial':
                this.clearDisplay()
                this.clearControls()
        
                this.addMessage('Press the start button to start recording')
                this.addButton('record', this.record, 'Start Recording')
                break;
    
            case 'Record':
                this.clearDisplay()
                this.clearControls()
    
                this.addMessage('Recording...')
                this.addButton('stop', this.stopRecording, 'Stop Recording')
                break
    
            case 'Download':
                /// ?
                this.clearControls()
                this.clearDisplay()
        
                this.addAudio()
                this.addButton('download', this.downloadAudio, 'Download Audio')
                this.addButton('record', this.record, 'Record Again')
                break
            
            default:
                this.clearControls()
                this.clearDisplay()
    
                this.addMessage('Your browser does not support mediaDevices')
                break;
        }
    
    }

    startApp = () => {
        this.display = document.querySelector('.audio-response-display');
        if(this.display != undefined){
            this.controllerWrapper = document.querySelector('.audio-response-controllers');
            this.application(this.stateIndex);
        }
    }
}

export default AudioRecord;