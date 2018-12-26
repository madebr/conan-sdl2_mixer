#include <SDL2/SDL.h>
#include <SDL2/SDL_mixer.h>

#include <cstdio>
#include <cstdlib>
#include <cstdarg>

void myerror(const char *fmt, ...) {
    va_list args;
    va_start(args, fmt);
    vprintf(fmt, args);
    va_end(args);
    exit(1);
}

// sine was generated using:
// ffmpeg -f lavfi -i "sine=frequency=440:duration=2" -ar 12000 -c:a adpcm_ima_wav sine.wav -y
#define SINE_WAV "sine.wav"

int main() {
	if (SDL_Init(SDL_INIT_AUDIO) < 0) {
	    myerror("SDL_Init failed\n");
    }

    const int flags = 0x0;
    const int initted = Mix_Init(flags);
    if (flags != initted) {
        myerror("Mix_init failed. Got 0x%x. (exptected 0x%x)\n", initted, flags);
    }
    if (Mix_OpenAudio(22050, MIX_DEFAULT_FORMAT, 2, 4096) == -1) {
        myerror("Mix_OpenAudio failed: %s\n", Mix_GetError());
    }

    const SDL_version *mix_ver = Mix_Linked_Version();
    printf("SDL2_mixer version %d.%d.%d\n", mix_ver->major, mix_ver->minor, mix_ver->patch);

    const int nbChunkDecoders = Mix_GetNumChunkDecoders();
    printf("Number of chunk decoders: %d\n", nbChunkDecoders);
    for (int i = 0; i < nbChunkDecoders; ++i) {
        printf("%2d - %s\n", i, Mix_GetChunkDecoder(i));
    }

    const int numchans = 4;
    int numactualchans = Mix_AllocateChannels(numchans);
    if (numchans != numactualchans) {
        myerror("Mix_AllocateChannels(%d) failed: expected %d, got %d\n", numchans, numchans, numactualchans);
    }
    if (Mix_Volume(0, MIX_MAX_VOLUME) == -1) {
        myerror("Mix_Volume failed: %s\n", Mix_GetError());
    }

    Mix_Chunk *wave = Mix_LoadWAV(SINE_WAV);
    if (wave == NULL) {
        myerror("Mix_LoadWAV(\"%s\") failed: %s\n", SINE_WAV, Mix_GetError());
    }
    if (Mix_VolumeChunk(wave, MIX_MAX_VOLUME) == -1) {
        myerror("Mix_VolumeChunk failed: %s\n", Mix_GetError());
    }

    if (Mix_PlayChannel(0, wave, 1) == -1) {
        myerror("Mix_PlayChannel failed: %s\n", Mix_GetError());
    }

    while (Mix_Playing(0)) {
    }

    Mix_FreeChunk(wave);

    Mix_CloseAudio();
    Mix_Quit();
    SDL_Quit();
    return EXIT_SUCCESS;
}
