interface ElevenLabsVoiceResponse {
  voice_id: string;
  name: string;
  samples: any[];
  category: string;
  fine_tuning: {
    is_allowed_to_fine_tune: boolean;
    state: string;
    verification_failures: string[];
    verification_attempts_count: number;
    manual_verification_requested: boolean;
  };
  labels: Record<string, string>;
  description: string;
  preview_url: string;
  available_for_tiers: string[];
  settings: {
    stability: number;
    similarity_boost: number;
    style: number;
    use_speaker_boost: boolean;
  };
  sharing: {
    status: string;
    history_item_sample_id: string;
    original_voice_id: string;
    public_owner_id: string;
    liked_by_count: number;
    cloned_by_count: number;
    name: string;
    description: string;
    labels: Record<string, string>;
    created_at: string;
  };
  high_quality_base_model_ids: string[];
  safety_control: string;
  voice_verification: {
    requires_verification: boolean;
    is_verified: boolean;
    verification_failures: string[];
    verification_attempts_count: number;
    language: string;
    accent: string;
  };
  owner_id: string;
  permission_on_resource: string;
}

interface VoiceCloneRequest {
  name: string;
  description?: string;
  labels?: Record<string, string>;
}

interface VoiceGenerationRequest {
  text: string;
  voice_settings?: {
    stability: number;
    similarity_boost: number;
    style?: number;
    use_speaker_boost?: boolean;
  };
}

class VoiceService {
  private readonly API_BASE = 'https://api.elevenlabs.io/v1';
  private readonly API_KEY = import.meta.env.VITE_ELEVENLABS_API_KEY;

  private getHeaders(): HeadersInit {
    return {
      'Accept': 'application/json',
      'xi-api-key': this.API_KEY,
    };
  }

  private getHeadersWithContentType(): HeadersInit {
    return {
      ...this.getHeaders(),
      'Content-Type': 'application/json',
    };
  }

  async createVoiceFromRecording(
    audioFile: File, 
    request: VoiceCloneRequest
  ): Promise<ElevenLabsVoiceResponse> {
    if (!this.API_KEY || this.API_KEY === 'your_elevenlabs_api_key_here') {
      throw new Error('ElevenLabs API key not configured');
    }

    const formData = new FormData();
    formData.append('name', request.name);
    
    if (request.description) {
      formData.append('description', request.description);
    }
    
    if (request.labels) {
      formData.append('labels', JSON.stringify(request.labels));
    }
    
    formData.append('files', audioFile);

    const response = await fetch(`${this.API_BASE}/voices/add`, {
      method: 'POST',
      headers: {
        'Accept': 'application/json',
        'xi-api-key': this.API_KEY,
      },
      body: formData,
    });

    if (!response.ok) {
      const errorData = await response.text();
      throw new Error(`Voice creation failed: ${response.status} - ${errorData}`);
    }

    return await response.json();
  }

  async generateSpeech(
    voiceId: string, 
    request: VoiceGenerationRequest
  ): Promise<ArrayBuffer> {
    if (!this.API_KEY || this.API_KEY === 'your_elevenlabs_api_key_here') {
      throw new Error('ElevenLabs API key not configured');
    }

    const response = await fetch(`${this.API_BASE}/text-to-speech/${voiceId}`, {
      method: 'POST',
      headers: this.getHeadersWithContentType(),
      body: JSON.stringify({
        text: request.text,
        model_id: 'eleven_monolingual_v1',
        voice_settings: {
          stability: 0.5,
          similarity_boost: 0.5,
          style: 0.0,
          use_speaker_boost: true,
          ...request.voice_settings
        }
      }),
    });

    if (!response.ok) {
      const errorData = await response.text();
      throw new Error(`Speech generation failed: ${response.status} - ${errorData}`);
    }

    return await response.arrayBuffer();
  }

  async getVoices(): Promise<{ voices: ElevenLabsVoiceResponse[] }> {
    if (!this.API_KEY || this.API_KEY === 'your_elevenlabs_api_key_here') {
      throw new Error('ElevenLabs API key not configured');
    }

    const response = await fetch(`${this.API_BASE}/voices`, {
      method: 'GET',
      headers: this.getHeaders(),
    });

    if (!response.ok) {
      const errorData = await response.text();
      throw new Error(`Failed to fetch voices: ${response.status} - ${errorData}`);
    }

    return await response.json();
  }

  async deleteVoice(voiceId: string): Promise<void> {
    if (!this.API_KEY || this.API_KEY === 'your_elevenlabs_api_key_here') {
      throw new Error('ElevenLabs API key not configured');
    }

    const response = await fetch(`${this.API_BASE}/voices/${voiceId}`, {
      method: 'DELETE',
      headers: this.getHeaders(),
    });

    if (!response.ok) {
      const errorData = await response.text();
      throw new Error(`Voice deletion failed: ${response.status} - ${errorData}`);
    }
  }

  async getVoiceById(voiceId: string): Promise<ElevenLabsVoiceResponse> {
    if (!this.API_KEY || this.API_KEY === 'your_elevenlabs_api_key_here') {
      throw new Error('ElevenLabs API key not configured');
    }

    const response = await fetch(`${this.API_BASE}/voices/${voiceId}`, {
      method: 'GET',
      headers: this.getHeaders(),
    });

    if (!response.ok) {
      const errorData = await response.text();
      throw new Error(`Failed to fetch voice: ${response.status} - ${errorData}`);
    }

    return await response.json();
  }

  createAudioUrl(audioBuffer: ArrayBuffer): string {
    const blob = new Blob([audioBuffer], { type: 'audio/mpeg' });
    return URL.createObjectURL(blob);
  }

  revokeAudioUrl(url: string): void {
    URL.revokeObjectURL(url);
  }

  // Generate speech using a specific voice ID (for premade voices like Nanay Avelina Gonzales)
  async generateSpeechWithVoiceId(
    text: string, 
    voiceId: string = 'HXiggO6rHDAxWaFMzhB7', // Nanay Avelina Gonzales - Filipino mother voice
    voiceSettings?: {
      stability?: number;
      similarity_boost?: number;
      style?: number;
      use_speaker_boost?: boolean;
    }
  ): Promise<ArrayBuffer> {
    if (!this.API_KEY || this.API_KEY === 'your_elevenlabs_api_key_here') {
      throw new Error('ElevenLabs API key not configured');
    }

    const response = await fetch(`${this.API_BASE}/text-to-speech/${voiceId}`, {
      method: 'POST',
      headers: this.getHeadersWithContentType(),
      body: JSON.stringify({
        text: text,
        model_id: 'eleven_monolingual_v1',
        voice_settings: {
          stability: 0.6,
          similarity_boost: 0.7,
          style: 0.1,
          use_speaker_boost: true,
          ...voiceSettings
        }
      }),
    });

    if (!response.ok) {
      const errorData = await response.text();
      throw new Error(`Speech generation failed: ${response.status} - ${errorData}`);
    }

    return await response.arrayBuffer();
  }
}

export const voiceService = new VoiceService();
export type { VoiceCloneRequest, VoiceGenerationRequest, ElevenLabsVoiceResponse };