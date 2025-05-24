# Audio Configurations //////////////////////////////////////////////////////////////////////////////
USER_AUDIO_SAMPLE_RATE       = 8000
USER_AUDIO_SECS_PER_CHUNK    = 0.05
USER_AUDIO_SAMPLES_PER_CHUNK = round(USER_AUDIO_SAMPLE_RATE * USER_AUDIO_SECS_PER_CHUNK)
CHANNELS                     = 1
ENCODING_                    = "mulaw"


# Speech 2 Text API Parameters/Configurations //////////////////////////////////////////////////////
STT_CONFIGURATION = dict(
    model            = "nova-3",
    language         = "en-US",
    smart_format     = True,
    encoding         = ENCODING_,
    interim_results  = True,
    sample_rate      = USER_AUDIO_SAMPLE_RATE,
    channels         = 1,
    no_delay         = True,
    utterance_end_ms = "1000",
    vad_events       = True,
    dictation        = True,
    punctuate        = True,
    filler_words     = True,
    numerals         = True,
)


# LLM API Paramters/Configurations /////////////////////////////////////////////////////////////////
PROVIDER          = "google"
MODEL             = "gemini-2.0-flash-lite"
LLM_CONFIGURATION = {"temperature":0.2}


# Text 2 Speech Parameters/Configurations //////////////////////////////////////////////////////////
TTS_CONFIGURATION = dict(
    model       = "aura-stella-en",
    encoding    = ENCODING_,
    sample_rate = USER_AUDIO_SAMPLE_RATE,
)