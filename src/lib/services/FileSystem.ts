import {
    create,
    writeTextFile,
    readTextFile,
    exists,
    truncate,
    BaseDirectory,
    mkdir,
} from "@tauri-apps/plugin-fs";
import * as path from '@tauri-apps/api/path';

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
        return this.name;
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

        const isDirExists = await exists(this._fullpath);
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
}

const home = await path.homeDir();
const ROOT_DIR = await path.join(home, '.' + import.meta.env.APP_NAME);
const BASE_STRUCTURE = new DirObject(
    ROOT_DIR,
    [
        new FileObject("preferences.json"),
    ]
);

export class FileSystem {
    private static _instance: FileSystem;
    private _root: DirObject = BASE_STRUCTURE;

    private constructor() {
    }

    public static get Instance() {
        return this._instance || (this._instance = new this());
    }

    get root(): DirObject {
        if (!this._root) {
            throw new Error("FileSystem has not been initialized yet.");
        }
        return this._root;
    }

    public async initialize(
        obj: FileObject | DirObject,
        parentPath: string = "",
        removeExists: boolean = false
    ): Promise<void> {
        const fullpath = await path.join(parentPath, obj.name);

        if (obj instanceof DirObject) {
            obj.create(fullpath, removeExists);
            for(const child of obj.children || []) {
                this.initialize(child, fullpath);
            }
        } else if (obj instanceof FileObject) {
            obj.create(fullpath, removeExists);
        }
    }

    public async reset(): Promise<void> {
        this._root = BASE_STRUCTURE;
        this.initialize(this._root, "", true);
    }

    // Base FileObject/DirObject methods.

    public get_preferences(): FileObject {
        if (!this._root.children)
            throw new Error("Root does not have any children.");

        return this._root.children.find(
            child => child instanceof FileObject && child.name === "preferences.json"
        ) as FileObject;
    }
}
