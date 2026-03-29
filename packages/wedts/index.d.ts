export declare function encryptText(passphrase: string, plaintext: string): string;

export declare function decryptText(passphrase: string, token: string): string;

export declare function encryptJson(passphrase: string, value: unknown): string;

export declare function decryptJson<T = unknown>(passphrase: string, token: string): T;
