
export default class ImageSelector {
    constructor() {
        this.id = Math.random();
        this.imgs = [];
    }

    /**
     * @param {HTMLImageElement} img 
     */
    push(img) {
        this.imgs.push(img.src);
    }

    toHtmlElement() {
        const div = document.createElement('div');
        div.innerHTML = template(this.id, this.imgs);
        const ret = div.firstChild;
        $('' + this.id).carousel();
        return ret;
    }
}

const template = (id, imgs) => {
    return '' +
`<div class="difference">
    <div id="${id}" class="carousel">
        <ol class="custom-indicators">${imgs.map((_, i) => `
            <li data-target="#${id}" data-slide-to="${i}"${i==0?' class="active"':''}>
                ${i + 1}
            </li>`).reduce((prev, cur) => prev + cur, '')}
        </ol>
        <div class="carousel-inner">${imgs.map((img, i) => `
            <div class="carousel-item${i == 0 ? ' active' : ''}">
                <img class="img-fluid rounded" src="${img}">
            </div>`).reduce((prev, cur) => prev + cur, '')}
        </div>
        <a class="carousel-control-prev" href="#${id}" role="button" data-slide="prev">
            <i class="fa fa-chevron-left"></i>
        </a>
        <a class="carousel-control-next" href="#${id}" role="button" data-slide="next">
            <i class="fa fa-chevron-right"></i>
        </a>
    </div>
</div>`
}
