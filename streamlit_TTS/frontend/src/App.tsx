import {
    Streamlit,
    StreamlitComponentBase,
    withStreamlitConnection,
} from "streamlit-component-lib"
import React, { ReactNode } from "react"
import './App.css'

const AudioPlayer: React.FC<{ audioBase64: string }> = ({ audioBase64 }) => {
  const audioRef = React.useRef<HTMLAudioElement | null>(null);

  React.useEffect(() => {
    Streamlit.setFrameHeight(0);

    if (!audioBase64) return;

    // Clean up previous audio instance
    if (audioRef.current) {
      audioRef.current.pause();
      audioRef.current.src = '';
      audioRef.current = null;
    }

    // Create new audio element
    const audio = new Audio();
    audioRef.current = audio;

    // Set audio properties for better cross-browser compatibility
    audio.preload = 'auto';
    audio.volume = 1.0;

    // Add multiple format support - browsers may prefer different formats
    audio.src = `data:audio/wav;base64,${audioBase64}`;

    // Handle successful playback
    const handleCanPlay = () => {
      audio.play().catch((error) => {
        console.warn('Autoplay failed, attempting workaround:', error);

        // Fallback 1: Try playing with lower volume
        audio.volume = 0.5;
        audio.play().catch((fallbackError) => {
          console.error('Audio playback failed:', fallbackError);

          // Fallback 2: Try with muted first, then unmute
          audio.muted = true;
          audio.play().then(() => {
            audio.muted = false;
          }).catch((finalError) => {
            console.error('All playback attempts failed:', finalError);
          });
        });
      });
    };

    // Handle errors during loading
    const handleError = (e: ErrorEvent) => {
      console.error('Audio loading error:', e);
    };

    // Attach event listeners
    audio.addEventListener('canplay', handleCanPlay);
    audio.addEventListener('error', handleError as any);

    // Start loading the audio
    audio.load();

    // Cleanup function
    return () => {
      audio.removeEventListener('canplay', handleCanPlay);
      audio.removeEventListener('error', handleError as any);
      audio.pause();
      audio.src = '';
      audioRef.current = null;
    };
  }, [audioBase64]);

  return null; // Ensure nothing is rendered on the page
}

interface State {}

class AutoPlay extends StreamlitComponentBase<State> {
    public state = {}

    public render = (): ReactNode => {
        const audioBase64 = this.props.args.audio_base64;

        return (
            <AudioPlayer audioBase64={audioBase64} />
        );
    }
}

export default withStreamlitConnection(AutoPlay);
