import 'babel-polyfill';

import ImageSelector from './image-selector';
import InlineSelector from './inline-selector';
import { vers } from './util';

window.onload = async () => {
    const container = document.querySelector('#diff-container');
    container.innerHTML = await (await fetch('diff.html')).text();
    document.querySelectorAll('.text-wrapper').forEach(text => {
        // wrap same versions
        let newChildren = [];
        [...text.children].forEach(child => {
            if (newChildren.length && vers(last(newChildren)) == vers(child)) {
                last(newChildren).innerHTML += child.innerHTML;
            } else {
                newChildren.push(child);
            }
        });
        text.innerHTML = '';
        newChildren.forEach(child => text.appendChild(child));
        
        // add inline selectors
        newChildren = [];
        [...text.children].forEach(child => {
            if (vers(text) == vers(child)) {
                newChildren.push(child);
            } else if (newChildren.length &&
                    last(newChildren) instanceof InlineSelector &&
                    !last(newChildren).anyOf(vers(child))) {
                last(newChildren).push(child);
            } else {
                const selector = new InlineSelector();
                selector.push(child);
                newChildren.push(selector);
            }
            text.removeChild(child);
        });
        newChildren.forEach(child => {
            text.appendChild(
                child instanceof InlineSelector ?
                child.toHtmlElement() : child
            );
        });
    });

    const rt = root();
    rt.parentNode.replaceChild(collectCarousels(rt), rt);

    applyDifferenceClass(root());

    document.querySelectorAll('tr').forEach(row => {
        const cells = Object.freeze([
            ...row.querySelectorAll('td'),
            ...row.querySelectorAll('th')
        ]);
        //
    });
}

function last(arr) {
    return arr[arr.length - 1];
}

function root() {
    return document.querySelector('.root');
}

/**
 * @param {HTMLElement} el 
 */
function collectCarousels(el) {
    const newChildren = [];
    [...el.children].forEach(child => {
        if (newChildren.length &&
                last(newChildren) instanceof ImageSelector &&
                child instanceof HTMLImageElement) {
            last(newChildren).push(child);
        } else if (child instanceof HTMLImageElement) {
            newChildren.push(new ImageSelector());
            last(newChildren).push(child);
        } else {
            newChildren.push(collectCarousels(child));
        }
        el.removeChild(child);
    });
    newChildren.forEach(child => {
        el.appendChild(
            child instanceof ImageSelector ?
            child.toHtmlElement() : child
        );
    });
    return el.cloneNode(true);
}

/**
 * @param {HTMLElement} el 
 */
function applyDifferenceClass(el) {
    [...el.children].forEach(child => {
        if (vers(el) != vers(child) && vers(child)) {
            child.classList.add('difference');
        } else {
            applyDifferenceClass(child);
        }
    });
}
