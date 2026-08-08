// APBattleView.js -- reads this view's own root ViewModel (APBattleVM: armorText,
// probText, angleText, color, visible) and paints the three label rows already
// in the HTML. No feature name in ModelObserver(): this page IS the view's root
// model (a standalone registered window), not a submodel injected into someone
// else's document.
// Two folder segments under mods/ (pademinune/APCalculator/) -> two "../" to libs/model.js.
import { ModelObserver } from "../../libs/model.js";

const observer = ModelObserver();

const armorEl = document.getElementById("armor-label");
const probEl = document.getElementById("prob-label");
const angleEl = document.getElementById("angle-label");
const bgEl = document.getElementById("label-bg");

function render(model) {
    // visible arrives as the string "true"/"false" (see setVisible in
    // mod_APBattleView.py) -- default to hidden if the model hasn't loaded yet.
    const visible = !!model && model.visible === "true";
    document.body.style.display = visible ? "" : "none";
    if (!visible) {
        return;
    }

    armorEl.textContent = model.armorText || "";
    probEl.textContent = model.probText || "";
    angleEl.textContent = model.angleText || "";

    const color = model.color ? "#" + model.color : "";
    armorEl.style.color = color;
    probEl.style.color = color;
    angleEl.style.color = color;
    bgEl.style.borderColor = color ? color + "59" : ""; // ~35% alpha, matches the default CSS border
}

engine.whenReady.then(() => {
    observer.onUpdate(render);   // called every time Python pushes a change
    observer.subscribe();
    render(observer.model);      // paint immediately with whatever's there now
});
