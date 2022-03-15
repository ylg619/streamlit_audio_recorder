import base64
import streamlit as st
from bokeh.models.widgets import Button
from bokeh.models import CustomJS
from streamlit_bokeh_events import streamlit_bokeh_events


stt_button  = Button(label="Speak", width=100)

stt_button.js_on_event("button_click", CustomJS(code="""
//Fiwed Time of Recording
const timeMilliSec = 5000 //Fixed 5sec records ... change here the value
navigator.mediaDevices.getUserMedia({ audio: true })
  .then(stream => {
    const mediaRecorder = new MediaRecorder(stream);
    mediaRecorder.start();
    const audioChunks = [];

    mediaRecorder.addEventListener("dataavailable", event => {
      audioChunks.push(event.data);
    });

    mediaRecorder.addEventListener("stop", () => {
      //convert audioBuffer to wav
      const audioBlob = new Blob(audioChunks, {type:'audio/wav'});
      //create base64 reader
      var reader = new FileReader();
      reader.readAsDataURL(audioBlob);
      reader.onloadend = function() {
        //read base64
        var base64data = reader.result;
        //send data to streamlit
        document.dispatchEvent(new CustomEvent("GET_AUDIO_BASE64", {detail: base64data}));
      }
    });

    setTimeout(() => {
      mediaRecorder.stop();
    }, timeMilliSec);
  });
  """))

result = streamlit_bokeh_events(
    stt_button,
    events="GET_AUDIO_BASE64",
    key="listen",
    refresh_on_update=False,
    override_height=75,
    debounce_time=0)

if result:
    if "GET_AUDIO_BASE64" in result:
        b64_str_metadata = result.get("GET_AUDIO_BASE64")
        #get rid of metadata (data:audio/wav;base64,)
        b64_str = b64_str_metadata.split('base64,')[1]
        decoded = base64.b64decode(b64_str)

        #save it server side if needed
        with open('test.wav','wb') as f:
            f.write(decoded)

        #Or read directly wav file in front
        st.audio(decoded)
