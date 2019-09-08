import { vers } from "./util";

export default class InlineSelector {
    constructor() {
        this.div = document.createElement('span');
        this.div.classList.add('inline-difference');
        this.vers = new Set();
    }

    /**
     * @param {string} vers 
     */
    anyOf(vers) {
        return vers.split(',').some(
            version => this.vers.has(version)
        );
    }

    /**
     * @returns {boolean}
     */
    empty() {
        return this.vers.size == 0;
    }

    /**
     * @param {HTMLElement} el 
     */
    push(el) {
        vers(el).split(',').forEach(version => this.vers.add(version));
        const node = el.cloneNode(true);
        node.innerText = node.innerText.trim();
        this.div.appendChild(node);
    }

    /**
     * @returns {HTMLElement}
     */
    toHtmlElement() {
        return this.div;
    }
}
