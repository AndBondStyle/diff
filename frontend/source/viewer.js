import 'babel-polyfill';

import InlineSelector from './inline-selector';
import { vers } from './util';

window.onload = async () => {
    const container = document.querySelector('#diff-container');
    container.innerHTML = await (await fetch('diff.html')).text();
    document.querySelectorAll('.text-wrapper').forEach(text => {
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
        
        newChildren = [];
        [...text.children].forEach(child => {
            if (newChildren.length &&
                    last(newChildren) instanceof InlineSelector &&
                    !last(newChildren).anyOf(vers(child))) {
                last(newChildren).push(child);
            } else if (vers(root()) == vers(child)) {
                newChildren.push(child);
            } else {
                const selector = new InlineSelector();
                selector.push(child);
                newChildren.push(selector);
            }
        });
        text.innerHTML = '';
        newChildren.forEach(child => {
            text.appendChild(
                child instanceof InlineSelector ?
                child.toHtmlElement() : child
            );
        });
    });

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
