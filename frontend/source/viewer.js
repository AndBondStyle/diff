import 'babel-polyfill';

window.onload = async () => {
    // const versions = document.body.getAttribute('data-ver').split(',');
    // const hues = versions.map(value => (2 * value + 1) / (2 * versions.length) * 360)
    const container = document.querySelector('#diff-container');
    container.innerHTML = await (await fetch('diff.html')).text();
    // document.querySelectorAll('.text-wrapper').forEach(text => {
    //     const newChildren = [text.children[0]];
    //     for (let i = 1; i < text.children.length; ++i) {
    //         if (newChildren[newChildren.length - 1].getAttribute('data-ver') ===
    //                 text.children[i].getAttribute('data-ver')) {
    //             newChildren[newChildren.length - 1].innerHTML += text.children[i].innerHTML;
    //         } else {
    //             newChildren.push(text.children[i]);
    //         }
    //     }
    //     text.innerHTML = '';
    //     newChildren.forEach(child => text.appendChild(child));
    // });
}
