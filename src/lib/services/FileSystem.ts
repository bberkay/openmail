import {
    create,
    writeTextFile,
    readTextFile,
    exists,
    truncate,
    mkdir,
    BaseDirectory
} from "@tauri-apps/plugin-fs";
import * as path from '@tauri-apps/api/path';
import type { Preferences } from "$lib/types";
import { SharedStore } from "$lib/stores/shared.svelte";
import { PUBLIC_APP_NAME } from "$env/static/public";

class FileNotFoundError extends Error {
    constructor(message: string = "File could not found.") {
        super(message);
        this.name = "FileNotFoundError";
    }
}

class DirNotFoundError extends Error {
    constructor(message: string = "Directory could not found.") {
        super(message);
        this.name = "DirNotFoundError";
    }
}

export class FileObject {
    private _name: string;
    private _initialContent: string;
    private _fullpath: string;

    constructor(name: string, initialContent: string = "") {
        this._name = name;
        this._initialContent = initialContent;
        this._fullpath = "";
    }

    toString() {
        return `Person(name='${this._name}')`;
    }

    get name() {
        return this._name;
    }

    get fullpath() {
        if (!this._fullpath) {
            throw new FileNotFoundError();
        }
        return this._fullpath;
    }

    public async create(
        fullpath: string,
        overwrite: boolean = false,
    ): Promise<void> {
        this._fullpath = fullpath;

        const isFileExists = await exists(this.fullpath);
        if (!overwrite && isFileExists) return;

        const file = await create(this.fullpath);
        await file.write(new TextEncoder().encode(this._initialContent));
        await file.close();
    }

    public async read(): Promise<string> {
        return await readTextFile(this.fullpath);
    }

    public async write(content: string): Promise<void> {
        await writeTextFile(this.fullpath, content);
    }

    public async clear(): Promise<void> {
        await truncate(this.fullpath, 0);
    }
}

export class DirObject {
    private _name: string;
    private _children: (FileObject | DirObject)[] | null;
    private _fullpath: string;

    constructor(name: string, children: (FileObject | DirObject)[] | null = null) {
        this._name = name;
        this._children = children;
        this._fullpath = "";
    }

    toString() {
        return `DirObject(name='${this.name}')`;
    }

    get name(): string {
        return this._name;
    }

    get fullpath(): string {
        if (!this._fullpath) {
            throw new DirNotFoundError();
        }
        return this._fullpath;
    }

    get children(): (FileObject | DirObject)[] | null {
        return this._children;
    }

    public async create(fullpath: string, overwrite: boolean = false): Promise<void> {
        this._fullpath = fullpath;

        const isDirExists = await exists(this.fullpath);
        if (!overwrite && isDirExists)
            return;

        await mkdir(this.fullpath);
    }

    public display(indent: number = 0): void {
        const prefix = " ".repeat(indent * 4) + (indent > 0 ? "└── " : "");
        console.log(`${prefix}${this.name}/`);

        for (const child of this._children || []) {
            if (child instanceof DirObject) {
                child.display(indent + 1);
            } else if (child instanceof FileObject) {
                const filePrefix = " ".repeat((indent + 1) * 4) + "└── ";
                console.log(`${filePrefix}${child.name}`);
            }
        }
    }

    public findChild(name: string): FileObject | DirObject | undefined {
        if (!this._children) return;

        const found = this._children.find(
            child => child.name === name
        );

        return found;
    }
}

async function setupFileSystem(): Promise<DirObject> {
    // Check out src-tauri/capabilities/default.json to set permissions of
    // current structure.
    const home = await path.homeDir();
    const rootDir = await path.join(home, '.' + PUBLIC_APP_NAME.toLowerCase(), "client");

    return new DirObject(
        rootDir,
        [
            new FileObject("preferences.json", "{}")
        ]
    );
}

export class FileSystem {
    private static _instance: FileSystem | null = null;
    private static _initializing: Promise<FileSystem> | null = null;
    private _root: DirObject | null = null;

    private constructor() {}

    /**
     * Get the singleton instance of FileSystem
     * If not already initialized, it will initialize
     */
    public static async getInstance(): Promise<FileSystem> {
        if (this._instance) {
            return this._instance;
        }

        if (this._initializing) {
            return this._initializing;
        }

        this._initializing = (async () => {
            const instance = new FileSystem();
            const rootStructure = await setupFileSystem();
            instance._root = rootStructure;
            await instance._initialize();
            this._instance = instance;
            this._initializing = null;
            return instance;
        })();

        return this._initializing;
    }

    get root(): DirObject {
        if (!this._root) {
            throw new Error("FileSystem has not been initialized yet.");
        }
        return this._root;
    }

    private async _initialize(
        obj?: FileObject | DirObject,
        parentPath: string = "",
        removeExists: boolean = false
    ): Promise<void> {
        const target = obj || this._root;

        if (!target) {
            throw new Error("No object provided and root is not initialized");
        }

        const fullpath = parentPath ?
            await path.join(parentPath, target.name) :
            target.name;

        if (target instanceof DirObject) {
            await target.create(fullpath, removeExists);

            if (target.children) {
                for (const child of target.children) {
                    await this._initialize(child, fullpath, removeExists);
                }
            }
        } else if (target instanceof FileObject) {
            await target.create(fullpath, removeExists);
        }
    }

    public async reset(): Promise<void> {
        if (!this._root) {
            throw new Error("FileSystem has not been initialized yet.");
        }

        await this._initialize(this._root, "", true);
    }

    public async download(filename: string, data: string): Promise<void> {
        const file = await create(filename, {
            baseDir: BaseDirectory.Download,
        });
        await file.write(
            Uint8Array.from(data, (char) =>
                char.charCodeAt(0),
            ),
        );
        await file.close();
    }

    // Base FileObject/DirObject methods.

    public getPreferences(): FileObject {
        if (!this._root)
            throw new Error("Root has not been initialized yet.");

        if (!this._root.children)
            throw new Error("Root does not have any children.");

        const prefsFile = this._root.findChild("preferences.json") as FileObject;

        if (!prefsFile)
            throw new FileNotFoundError("preferences.json file not found in root directory.");

        return prefsFile;
    }

    public async readPreferences(): Promise<Preferences> {
        const prefsFile = this.getPreferences();
        const content = await prefsFile.read();

        return JSON.parse(content);
    }

    public async savePreferences(data: Partial<Preferences>): Promise<void> {
        SharedStore.preferences = { ...SharedStore.preferences, ...data };
        const prefsFile = this.getPreferences();
        await prefsFile.write(JSON.stringify(data, null, 2));
    }
}
