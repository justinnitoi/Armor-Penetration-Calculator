// APBattleView.js -- reads this view's own root ViewModel (APBattleVM: armorText,
// probText, angleText) and paints the three label rows already in the HTML. No
// feature name in ModelObserver(): this page IS the view's root model (a
// standalone registered window), not a submodel injected into someone else's
// document.
// Two folder segments under mods/ (pademinune/APCalculator/) -> two "../" to libs/model.js.
import { ModelObserver } from "../../libs/model.js";

const observer = ModelObserver();

function render(model) {
    // document.getElementById("armor-label").textContent = (model && model.armorText) || "";
    // document.getElementById("prob-label").textContent = (model && model.probText) || "";
    // document.getElementById("angle-label").textContent = (model && model.angleText) || "";
}

engine.whenReady.then(() => {
    observer.onUpdate(render);   // called every time Python pushes a change
    observer.subscribe();
    render(observer.model);      // paint immediately with whatever's there now
});
