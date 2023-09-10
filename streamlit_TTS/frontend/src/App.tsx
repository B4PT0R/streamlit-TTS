import {
  StreamlitComponentBase,
  withStreamlitConnection,
} from "streamlit-component-lib"
import React, { ReactNode } from "react"
import './App.css'

const AudioPlayer: React.FC<{ audioBase64: string }> = ({ audioBase64 }) => {
  React.useEffect(() => {
      if (audioBase64) {
          const audio = new Audio(`data:audio/wav;base64,${audioBase64}`);
          audio.play();
      }
  }, [audioBase64]);

  return null; // Ensure nothing is rendered on the page
}

interface State {}

class Component extends StreamlitComponentBase<State> {
    public state = {}

    public render = (): ReactNode => {
        const audioBase64 = this.props.args.audio_base64;

        return (
            <AudioPlayer audioBase64={audioBase64} />
        );
    }
}

export default withStreamlitConnection(Component);
