const L=globalThis,K=L.ShadowRoot&&(L.ShadyCSS===void 0||L.ShadyCSS.nativeShadow)&&"adoptedStyleSheets"in Document.prototype&&"replace"in CSSStyleSheet.prototype,Z=Symbol(),X=new WeakMap;let he=class{constructor(e,t,r){if(this._$cssResult$=!0,r!==Z)throw Error("CSSResult is not constructable. Use `unsafeCSS` or `css` instead.");this.cssText=e,this.t=t}get styleSheet(){let e=this.o;const t=this.t;if(K&&e===void 0){const r=t!==void 0&&t.length===1;r&&(e=X.get(t)),e===void 0&&((this.o=e=new CSSStyleSheet).replaceSync(this.cssText),r&&X.set(t,e))}return e}toString(){return this.cssText}};const Se=i=>new he(typeof i=="string"?i:i+"",void 0,Z),Ee=(i,...e)=>{const t=i.length===1?i[0]:e.reduce((r,n,s)=>r+(o=>{if(o._$cssResult$===!0)return o.cssText;if(typeof o=="number")return o;throw Error("Value passed to 'css' function must be a 'css' function result: "+o+". Use 'unsafeCSS' to pass non-literal values, but take care to ensure page security.")})(n)+i[s+1],i[0]);return new he(t,i,Z)},xe=(i,e)=>{if(K)i.adoptedStyleSheets=e.map(t=>t instanceof CSSStyleSheet?t:t.styleSheet);else for(const t of e){const r=document.createElement("style"),n=L.litNonce;n!==void 0&&r.setAttribute("nonce",n),r.textContent=t.cssText,i.appendChild(r)}},Y=K?i=>i:i=>i instanceof CSSStyleSheet?(e=>{let t="";for(const r of e.cssRules)t+=r.cssText;return Se(t)})(i):i;const{is:Ce,defineProperty:Ie,getOwnPropertyDescriptor:Re,getOwnPropertyNames:Pe,getOwnPropertySymbols:Ne,getPrototypeOf:Oe}=Object,_=globalThis,ee=_.trustedTypes,Me=ee?ee.emptyScript:"",ke=_.reactiveElementPolyfillSupport,x=(i,e)=>i,F={toAttribute(i,e){switch(e){case Boolean:i=i?Me:null;break;case Object:case Array:i=i==null?i:JSON.stringify(i)}return i},fromAttribute(i,e){let t=i;switch(e){case Boolean:t=i!==null;break;case Number:t=i===null?null:Number(i);break;case Object:case Array:try{t=JSON.parse(i)}catch{t=null}}return t}},pe=(i,e)=>!Ce(i,e),te={attribute:!0,type:String,converter:F,reflect:!1,useDefault:!1,hasChanged:pe};Symbol.metadata??(Symbol.metadata=Symbol("metadata")),_.litPropertyMetadata??(_.litPropertyMetadata=new WeakMap);let b=class extends HTMLElement{static addInitializer(e){this._$Ei(),(this.l??(this.l=[])).push(e)}static get observedAttributes(){return this.finalize(),this._$Eh&&[...this._$Eh.keys()]}static createProperty(e,t=te){if(t.state&&(t.attribute=!1),this._$Ei(),this.prototype.hasOwnProperty(e)&&((t=Object.create(t)).wrapped=!0),this.elementProperties.set(e,t),!t.noAccessor){const r=Symbol(),n=this.getPropertyDescriptor(e,r,t);n!==void 0&&Ie(this.prototype,e,n)}}static getPropertyDescriptor(e,t,r){const{get:n,set:s}=Re(this.prototype,e)??{get(){return this[t]},set(o){this[t]=o}};return{get:n,set(o){const l=n?.call(this);s?.call(this,o),this.requestUpdate(e,l,r)},configurable:!0,enumerable:!0}}static getPropertyOptions(e){return this.elementProperties.get(e)??te}static _$Ei(){if(this.hasOwnProperty(x("elementProperties")))return;const e=Oe(this);e.finalize(),e.l!==void 0&&(this.l=[...e.l]),this.elementProperties=new Map(e.elementProperties)}static finalize(){if(this.hasOwnProperty(x("finalized")))return;if(this.finalized=!0,this._$Ei(),this.hasOwnProperty(x("properties"))){const t=this.properties,r=[...Pe(t),...Ne(t)];for(const n of r)this.createProperty(n,t[n])}const e=this[Symbol.metadata];if(e!==null){const t=litPropertyMetadata.get(e);if(t!==void 0)for(const[r,n]of t)this.elementProperties.set(r,n)}this._$Eh=new Map;for(const[t,r]of this.elementProperties){const n=this._$Eu(t,r);n!==void 0&&this._$Eh.set(n,t)}this.elementStyles=this.finalizeStyles(this.styles)}static finalizeStyles(e){const t=[];if(Array.isArray(e)){const r=new Set(e.flat(1/0).reverse());for(const n of r)t.unshift(Y(n))}else e!==void 0&&t.push(Y(e));return t}static _$Eu(e,t){const r=t.attribute;return r===!1?void 0:typeof r=="string"?r:typeof e=="string"?e.toLowerCase():void 0}constructor(){super(),this._$Ep=void 0,this.isUpdatePending=!1,this.hasUpdated=!1,this._$Em=null,this._$Ev()}_$Ev(){this._$ES=new Promise(e=>this.enableUpdating=e),this._$AL=new Map,this._$E_(),this.requestUpdate(),this.constructor.l?.forEach(e=>e(this))}addController(e){(this._$EO??(this._$EO=new Set)).add(e),this.renderRoot!==void 0&&this.isConnected&&e.hostConnected?.()}removeController(e){this._$EO?.delete(e)}_$E_(){const e=new Map,t=this.constructor.elementProperties;for(const r of t.keys())this.hasOwnProperty(r)&&(e.set(r,this[r]),delete this[r]);e.size>0&&(this._$Ep=e)}createRenderRoot(){const e=this.shadowRoot??this.attachShadow(this.constructor.shadowRootOptions);return xe(e,this.constructor.elementStyles),e}connectedCallback(){this.renderRoot??(this.renderRoot=this.createRenderRoot()),this.enableUpdating(!0),this._$EO?.forEach(e=>e.hostConnected?.())}enableUpdating(e){}disconnectedCallback(){this._$EO?.forEach(e=>e.hostDisconnected?.())}attributeChangedCallback(e,t,r){this._$AK(e,r)}_$ET(e,t){const r=this.constructor.elementProperties.get(e),n=this.constructor._$Eu(e,r);if(n!==void 0&&r.reflect===!0){const s=(r.converter?.toAttribute!==void 0?r.converter:F).toAttribute(t,r.type);this._$Em=e,s==null?this.removeAttribute(n):this.setAttribute(n,s),this._$Em=null}}_$AK(e,t){const r=this.constructor,n=r._$Eh.get(e);if(n!==void 0&&this._$Em!==n){const s=r.getPropertyOptions(n),o=typeof s.converter=="function"?{fromAttribute:s.converter}:s.converter?.fromAttribute!==void 0?s.converter:F;this._$Em=n;const l=o.fromAttribute(t,s.type);this[n]=l??this._$Ej?.get(n)??l,this._$Em=null}}requestUpdate(e,t,r,n=!1,s){if(e!==void 0){const o=this.constructor;if(n===!1&&(s=this[e]),r??(r=o.getPropertyOptions(e)),!((r.hasChanged??pe)(s,t)||r.useDefault&&r.reflect&&s===this._$Ej?.get(e)&&!this.hasAttribute(o._$Eu(e,r))))return;this.C(e,t,r)}this.isUpdatePending===!1&&(this._$ES=this._$EP())}C(e,t,{useDefault:r,reflect:n,wrapped:s},o){r&&!(this._$Ej??(this._$Ej=new Map)).has(e)&&(this._$Ej.set(e,o??t??this[e]),s!==!0||o!==void 0)||(this._$AL.has(e)||(this.hasUpdated||r||(t=void 0),this._$AL.set(e,t)),n===!0&&this._$Em!==e&&(this._$Eq??(this._$Eq=new Set)).add(e))}async _$EP(){this.isUpdatePending=!0;try{await this._$ES}catch(t){Promise.reject(t)}const e=this.scheduleUpdate();return e!=null&&await e,!this.isUpdatePending}scheduleUpdate(){return this.performUpdate()}performUpdate(){if(!this.isUpdatePending)return;if(!this.hasUpdated){if(this.renderRoot??(this.renderRoot=this.createRenderRoot()),this._$Ep){for(const[n,s]of this._$Ep)this[n]=s;this._$Ep=void 0}const r=this.constructor.elementProperties;if(r.size>0)for(const[n,s]of r){const{wrapped:o}=s,l=this[n];o!==!0||this._$AL.has(n)||l===void 0||this.C(n,void 0,s,l)}}let e=!1;const t=this._$AL;try{e=this.shouldUpdate(t),e?(this.willUpdate(t),this._$EO?.forEach(r=>r.hostUpdate?.()),this.update(t)):this._$EM()}catch(r){throw e=!1,this._$EM(),r}e&&this._$AE(t)}willUpdate(e){}_$AE(e){this._$EO?.forEach(t=>t.hostUpdated?.()),this.hasUpdated||(this.hasUpdated=!0,this.firstUpdated(e)),this.updated(e)}_$EM(){this._$AL=new Map,this.isUpdatePending=!1}get updateComplete(){return this.getUpdateComplete()}getUpdateComplete(){return this._$ES}shouldUpdate(e){return!0}update(e){this._$Eq&&(this._$Eq=this._$Eq.forEach(t=>this._$ET(t,this[t]))),this._$EM()}updated(e){}firstUpdated(e){}};b.elementStyles=[],b.shadowRootOptions={mode:"open"},b[x("elementProperties")]=new Map,b[x("finalized")]=new Map,ke?.({ReactiveElement:b}),(_.reactiveElementVersions??(_.reactiveElementVersions=[])).push("2.1.2");const C=globalThis,re=i=>i,H=C.trustedTypes,ie=H?H.createPolicy("lit-html",{createHTML:i=>i}):void 0,me="$lit$",g=`lit$${Math.random().toFixed(9).slice(2)}$`,fe="?"+g,Ue=`<${fe}>`,y=document,P=()=>y.createComment(""),N=i=>i===null||typeof i!="object"&&typeof i!="function",J=Array.isArray,Te=i=>J(i)||typeof i?.[Symbol.iterator]=="function",B=`[ 	
\f\r]`,E=/<(?:(!--|\/[^a-zA-Z])|(\/?[a-zA-Z][^>\s]*)|(\/?$))/g,ne=/-->/g,se=/>/g,$=RegExp(`>|${B}(?:([^\\s"'>=/]+)(${B}*=${B}*(?:[^ 	
\f\r"'\`<>=]|("|')|))|$)`,"g"),oe=/'/g,ae=/"/g,ge=/^(?:script|style|textarea|title)$/i,Le=i=>(e,...t)=>({_$litType$:i,strings:e,values:t}),p=Le(1),w=Symbol.for("lit-noChange"),c=Symbol.for("lit-nothing"),le=new WeakMap,v=y.createTreeWalker(y,129);function _e(i,e){if(!J(i)||!i.hasOwnProperty("raw"))throw Error("invalid template strings array");return ie!==void 0?ie.createHTML(e):e}const He=(i,e)=>{const t=i.length-1,r=[];let n,s=e===2?"<svg>":e===3?"<math>":"",o=E;for(let l=0;l<t;l++){const a=i[l];let d,h,u=-1,m=0;for(;m<a.length&&(o.lastIndex=m,h=o.exec(a),h!==null);)m=o.lastIndex,o===E?h[1]==="!--"?o=ne:h[1]!==void 0?o=se:h[2]!==void 0?(ge.test(h[2])&&(n=RegExp("</"+h[2],"g")),o=$):h[3]!==void 0&&(o=$):o===$?h[0]===">"?(o=n??E,u=-1):h[1]===void 0?u=-2:(u=o.lastIndex-h[2].length,d=h[1],o=h[3]===void 0?$:h[3]==='"'?ae:oe):o===ae||o===oe?o=$:o===ne||o===se?o=E:(o=$,n=void 0);const f=o===$&&i[l+1].startsWith("/>")?" ":"";s+=o===E?a+Ue:u>=0?(r.push(d),a.slice(0,u)+me+a.slice(u)+g+f):a+g+(u===-2?l:f)}return[_e(i,s+(i[t]||"<?>")+(e===2?"</svg>":e===3?"</math>":"")),r]};class O{constructor({strings:e,_$litType$:t},r){let n;this.parts=[];let s=0,o=0;const l=e.length-1,a=this.parts,[d,h]=He(e,t);if(this.el=O.createElement(d,r),v.currentNode=this.el.content,t===2||t===3){const u=this.el.content.firstChild;u.replaceWith(...u.childNodes)}for(;(n=v.nextNode())!==null&&a.length<l;){if(n.nodeType===1){if(n.hasAttributes())for(const u of n.getAttributeNames())if(u.endsWith(me)){const m=h[o++],f=n.getAttribute(u).split(g),k=/([.?@])?(.*)/.exec(m);a.push({type:1,index:s,name:k[2],strings:f,ctor:k[1]==="."?qe:k[1]==="?"?De:k[1]==="@"?je:j}),n.removeAttribute(u)}else u.startsWith(g)&&(a.push({type:6,index:s}),n.removeAttribute(u));if(ge.test(n.tagName)){const u=n.textContent.split(g),m=u.length-1;if(m>0){n.textContent=H?H.emptyScript:"";for(let f=0;f<m;f++)n.append(u[f],P()),v.nextNode(),a.push({type:2,index:++s});n.append(u[m],P())}}}else if(n.nodeType===8)if(n.data===fe)a.push({type:2,index:s});else{let u=-1;for(;(u=n.data.indexOf(g,u+1))!==-1;)a.push({type:7,index:s}),u+=g.length-1}s++}}static createElement(e,t){const r=y.createElement("template");return r.innerHTML=e,r}}function S(i,e,t=i,r){if(e===w)return e;let n=r!==void 0?t._$Co?.[r]:t._$Cl;const s=N(e)?void 0:e._$litDirective$;return n?.constructor!==s&&(n?._$AO?.(!1),s===void 0?n=void 0:(n=new s(i),n._$AT(i,t,r)),r!==void 0?(t._$Co??(t._$Co=[]))[r]=n:t._$Cl=n),n!==void 0&&(e=S(i,n._$AS(i,e.values),n,r)),e}class ze{constructor(e,t){this._$AV=[],this._$AN=void 0,this._$AD=e,this._$AM=t}get parentNode(){return this._$AM.parentNode}get _$AU(){return this._$AM._$AU}u(e){const{el:{content:t},parts:r}=this._$AD,n=(e?.creationScope??y).importNode(t,!0);v.currentNode=n;let s=v.nextNode(),o=0,l=0,a=r[0];for(;a!==void 0;){if(o===a.index){let d;a.type===2?d=new M(s,s.nextSibling,this,e):a.type===1?d=new a.ctor(s,a.name,a.strings,this,e):a.type===6&&(d=new Be(s,this,e)),this._$AV.push(d),a=r[++l]}o!==a?.index&&(s=v.nextNode(),o++)}return v.currentNode=y,n}p(e){let t=0;for(const r of this._$AV)r!==void 0&&(r.strings!==void 0?(r._$AI(e,r,t),t+=r.strings.length-2):r._$AI(e[t])),t++}}class M{get _$AU(){return this._$AM?._$AU??this._$Cv}constructor(e,t,r,n){this.type=2,this._$AH=c,this._$AN=void 0,this._$AA=e,this._$AB=t,this._$AM=r,this.options=n,this._$Cv=n?.isConnected??!0}get parentNode(){let e=this._$AA.parentNode;const t=this._$AM;return t!==void 0&&e?.nodeType===11&&(e=t.parentNode),e}get startNode(){return this._$AA}get endNode(){return this._$AB}_$AI(e,t=this){e=S(this,e,t),N(e)?e===c||e==null||e===""?(this._$AH!==c&&this._$AR(),this._$AH=c):e!==this._$AH&&e!==w&&this._(e):e._$litType$!==void 0?this.$(e):e.nodeType!==void 0?this.T(e):Te(e)?this.k(e):this._(e)}O(e){return this._$AA.parentNode.insertBefore(e,this._$AB)}T(e){this._$AH!==e&&(this._$AR(),this._$AH=this.O(e))}_(e){this._$AH!==c&&N(this._$AH)?this._$AA.nextSibling.data=e:this.T(y.createTextNode(e)),this._$AH=e}$(e){const{values:t,_$litType$:r}=e,n=typeof r=="number"?this._$AC(e):(r.el===void 0&&(r.el=O.createElement(_e(r.h,r.h[0]),this.options)),r);if(this._$AH?._$AD===n)this._$AH.p(t);else{const s=new ze(n,this),o=s.u(this.options);s.p(t),this.T(o),this._$AH=s}}_$AC(e){let t=le.get(e.strings);return t===void 0&&le.set(e.strings,t=new O(e)),t}k(e){J(this._$AH)||(this._$AH=[],this._$AR());const t=this._$AH;let r,n=0;for(const s of e)n===t.length?t.push(r=new M(this.O(P()),this.O(P()),this,this.options)):r=t[n],r._$AI(s),n++;n<t.length&&(this._$AR(r&&r._$AB.nextSibling,n),t.length=n)}_$AR(e=this._$AA.nextSibling,t){for(this._$AP?.(!1,!0,t);e!==this._$AB;){const r=re(e).nextSibling;re(e).remove(),e=r}}setConnected(e){this._$AM===void 0&&(this._$Cv=e,this._$AP?.(e))}}class j{get tagName(){return this.element.tagName}get _$AU(){return this._$AM._$AU}constructor(e,t,r,n,s){this.type=1,this._$AH=c,this._$AN=void 0,this.element=e,this.name=t,this._$AM=n,this.options=s,r.length>2||r[0]!==""||r[1]!==""?(this._$AH=Array(r.length-1).fill(new String),this.strings=r):this._$AH=c}_$AI(e,t=this,r,n){const s=this.strings;let o=!1;if(s===void 0)e=S(this,e,t,0),o=!N(e)||e!==this._$AH&&e!==w,o&&(this._$AH=e);else{const l=e;let a,d;for(e=s[0],a=0;a<s.length-1;a++)d=S(this,l[r+a],t,a),d===w&&(d=this._$AH[a]),o||(o=!N(d)||d!==this._$AH[a]),d===c?e=c:e!==c&&(e+=(d??"")+s[a+1]),this._$AH[a]=d}o&&!n&&this.j(e)}j(e){e===c?this.element.removeAttribute(this.name):this.element.setAttribute(this.name,e??"")}}class qe extends j{constructor(){super(...arguments),this.type=3}j(e){this.element[this.name]=e===c?void 0:e}}class De extends j{constructor(){super(...arguments),this.type=4}j(e){this.element.toggleAttribute(this.name,!!e&&e!==c)}}class je extends j{constructor(e,t,r,n,s){super(e,t,r,n,s),this.type=5}_$AI(e,t=this){if((e=S(this,e,t,0)??c)===w)return;const r=this._$AH,n=e===c&&r!==c||e.capture!==r.capture||e.once!==r.once||e.passive!==r.passive,s=e!==c&&(r===c||n);n&&this.element.removeEventListener(this.name,this,r),s&&this.element.addEventListener(this.name,this,e),this._$AH=e}handleEvent(e){typeof this._$AH=="function"?this._$AH.call(this.options?.host??this.element,e):this._$AH.handleEvent(e)}}class Be{constructor(e,t,r){this.element=e,this.type=6,this._$AN=void 0,this._$AM=t,this.options=r}get _$AU(){return this._$AM._$AU}_$AI(e){S(this,e)}}const Ve=C.litHtmlPolyfillSupport;Ve?.(O,M),(C.litHtmlVersions??(C.litHtmlVersions=[])).push("3.3.3");const Qe=(i,e,t)=>{const r=t?.renderBefore??e;let n=r._$litPart$;if(n===void 0){const s=t?.renderBefore??null;r._$litPart$=n=new M(e.insertBefore(P(),s),s,void 0,t??{})}return n._$AI(i),n};const I=globalThis;class R extends b{constructor(){super(...arguments),this.renderOptions={host:this},this._$Do=void 0}createRenderRoot(){var t;const e=super.createRenderRoot();return(t=this.renderOptions).renderBefore??(t.renderBefore=e.firstChild),e}update(e){const t=this.render();this.hasUpdated||(this.renderOptions.isConnected=this.isConnected),super.update(e),this._$Do=Qe(t,this.renderRoot,this.renderOptions)}connectedCallback(){super.connectedCallback(),this._$Do?.setConnected(!0)}disconnectedCallback(){super.disconnectedCallback(),this._$Do?.setConnected(!1)}render(){return w}}R._$litElement$=!0,R.finalized=!0,I.litElementHydrateSupport?.({LitElement:R});const Fe=I.litElementPolyfillSupport;Fe?.({LitElement:R});(I.litElementVersions??(I.litElementVersions=[])).push("4.2.2");const We=new Set(["washing","washing_paused","clean_add_water","charging_completed","returning_to_wash","auto_emptying"]),Ge=new Set(["sweeping_and_mopping","sweeping","vacuuming","mopping","spot_cleaning","room_cleaning","segment_cleaning"]),Ke={water_tank_dry:"clean water tank empty",dirty_water_tank:"dirty water tank full",remove_mop:"remove mop pads",route:"route blocked"};function A(i){return String(i??"").trim().toLowerCase()}function $e(i){const e=A(i);return e?e.replaceAll("_"," "):""}function Ze(i){const e=A(i);return!e||e==="no_error"||e==="unknown"||e==="unavailable"?null:Ke[e]??$e(e)}function Je(i){switch(i){case"washing":return"Washing pads";case"washing_paused":return"Washing paused";case"clean_add_water":return"Adding water";case"returning_to_wash":return"Returning to wash";case"auto_emptying":return"Auto-emptying";default:return $e(i)}}function Xe(i){if(A(i.queueRunState)!=="running")return null;const e=A(i.vacuumState),t=A(i.robotState),r=A(i.taskStatus),n=Ze(i.errorCode);if(e==="error")return{phase:"error",label:n??"Error"};if(r==="completed")return{phase:"finishing",label:"Finishing step"};if(e==="paused")return{phase:"paused",label:n?`Paused (${n})`:"Paused"};if(We.has(t))return{phase:"preparing",label:Je(t)};if(e==="returning"&&r==="room_cleaning")return{phase:"returning",label:"Returning to base"};if(Ge.has(t))switch(t){case"sweeping":case"vacuuming":return{phase:"cleaning",label:"Vacuuming"};case"mopping":return{phase:"cleaning",label:"Mopping"};case"sweeping_and_mopping":return{phase:"cleaning",label:"Vacuuming + mopping"};case"spot_cleaning":return{phase:"cleaning",label:"Spot cleaning"};default:return{phase:"cleaning",label:"Cleaning room"}}return e==="cleaning"?{phase:"cleaning",label:"Cleaning room"}:e==="returning"?{phase:"returning",label:"Returning to base"}:{phase:"unknown",label:"Working"}}function V(i,e){const t=String(i||"").trim();if(!t.startsWith("vacuum."))return null;const r=t.slice(7);return r?`sensor.${r}_${e}`:null}function z(i){return typeof i=="object"&&i!==null&&!Array.isArray(i)}function Ye(i){return String(i??"").trim()}function ve(i){return Ye(i).toLowerCase()}function U(i){return typeof i!="number"||!Number.isFinite(i)||i<0?null:Math.trunc(i)}function Q(i,e){return i.filter(t=>t.status===e).length}function et(i){if(!z(i))return null;const e=i.item_id,t=i.room_id,r=i.room_name,n=i.status;return typeof e!="string"||typeof t!="number"||!Number.isFinite(t)||typeof r!="string"||typeof n!="string"?null:{itemId:e,roomId:t,roomName:r,status:n,overrides:z(i.overrides)?{...i.overrides}:{},result:typeof i.result=="string"?i.result:null}}function ye(i){const e=ve(i);return e?e==="blocked"?"Route blocked":e==="out_of_sync"?"Out of sync":e.charAt(0).toUpperCase()+e.slice(1):"Unknown"}function tt(i){if(!z(i))return[];const e=i.queue_items;return Array.isArray(e)?e.flatMap(t=>{const r=et(t);return r?[r]:[]}):[]}function rt(i){const e=i?.attributes,t=tt(e),r=z(e)?e:{};return{runState:ve(i?.state)||"unknown",configEntryId:typeof r.config_entry_id=="string"?r.config_entry_id:null,vacuumEntityId:typeof r.vacuum_entity_id=="string"?r.vacuum_entity_id:null,pendingItems:U(r.pending_items)??Q(t,"pending"),runningItems:U(r.running_items)??Q(t,"running"),completedItems:U(r.completed_items)??Q(t,"completed"),totalItems:U(r.total_items)??t.length,items:t}}const be={water_volume:[{value:0,label:"Off"},{value:1,label:"Min"},{value:2,label:"Med"},{value:3,label:"Max"}],suction_level:[{value:-1,label:"Off"},{value:0,label:"Min"},{value:1,label:"Med"},{value:2,label:"Max"},{value:3,label:"Turbo"}],repeats:[{value:1,label:"x1"},{value:2,label:"x2"},{value:3,label:"x3"}]},it={water_volume:2,suction_level:1,repeats:1};function Ae(i){if(i==null)return null;if(typeof i=="number")return Number.isFinite(i)?Math.trunc(i):null;if(typeof i=="string"){const e=Number(i.trim());return Number.isFinite(e)?Math.trunc(e):null}return null}function we(i,e){const t={};for(const[r,n]of Object.entries(e??{}))n!=null&&(t[r]=n);for(const[r,n]of Object.entries(i??{}))n!=null&&(t[r]=n);return t}function nt(i,e,t){const r=we(e,t);return Ae(r[i])??it[i]}function st(i,e,t){const r=nt(i,e,t),n=be[i].find(s=>s.value===r);return n?n.label:String(r)}function ot(i,e,t){const r=we(e,t),n=be[i],s=Ae(r[i]),o=n.findIndex(a=>a.value===s),l=o<0?0:(o+1)%n.length;return r[i]=n[l].value,r}function ce(i){if(typeof i=="number"&&Number.isInteger(i))return i;if(typeof i!="string")return null;const e=i.trim();if(!e)return null;const t=Number(e);return Number.isInteger(t)?t:null}function W(i,e){if(Array.isArray(i)){for(const s of i)W(s,e);return}if(typeof i!="object"||i===null)return;const t=i,r=ce(t.id),n=typeof t.name=="string"?t.name.trim():"";r!==null&&n&&e.push({roomId:r,roomName:n});for(const[s,o]of Object.entries(t)){const l=ce(s);if(l!==null&&typeof o=="string"){const a=o.trim();if(a){e.push({roomId:l,roomName:a});continue}}W(o,e)}}function at(i){const e=[];W(i,e);const t=new Map;for(const r of e)t.set(r.roomId,r.roomName);return Array.from(t.entries()).map(([r,n])=>({roomId:r,roomName:n})).sort((r,n)=>r.roomId-n.roomId)}const q="ha-dreame-queue-card",lt="HA Dreame Queue",ct=[{field:"water_volume",label:"Water"},{field:"suction_level",label:"Suction"},{field:"repeats",label:"Repeats"}];function ut(i,e){const t=de(e.title)||lt,r=de(e.entity)||null;if(!r)return ue({title:t,status:"not_configured",entityId:null,message:"Configure a HA Dreame queue status entity."});const n=i?.states[r];if(!n)return ue({title:t,status:"missing",entityId:r,message:"Queue entity not found."});const s=rt(n),o=dt(i,s),l=gt(i,s);return{title:t,status:"ready",entityId:r,message:null,summary:mt(s,o),snapshot:s,activity:o,activeControls:pt(s),canClearPending:s.pendingItems>0,rooms:l,rows:ht(s.items)}}function ue({title:i,status:e,entityId:t,message:r}){return{title:i,status:e,entityId:t,message:r,summary:null,snapshot:null,activity:null,activeControls:[],canClearPending:!1,rooms:[],rows:[]}}function dt(i,e){const t=e.vacuumEntityId;return!i||!t?null:Xe({queueRunState:e.runState,vacuumState:T(i,t),robotState:T(i,V(t,"state")),taskStatus:T(i,V(t,"task_status")),errorCode:T(i,V(t,"error"))})}function ht(i){const e=i.flatMap((n,s)=>n.status==="pending"?[s]:[]),t=e[0]??null,r=e[e.length-1]??null;return i.map((n,s)=>({itemId:n.itemId,queuePosition:s,roomName:n.roomName,status:n.status,statusLabel:ye(n.status),overrides:{...n.overrides},canRemove:n.status==="pending",canMoveUp:n.status==="pending"&&s!==t,canMoveDown:n.status==="pending"&&s!==r,overrideControls:n.status==="pending"?ft(n.overrides):[]}))}function pt(i){return i.runState==="running"?[{ariaLabel:"Cancel queue",label:"Cancel",service:"cancel_queue"},{ariaLabel:"Skip current room",label:"Skip",service:"skip_current_room"}]:i.runState==="idle"&&i.pendingItems>0?[{ariaLabel:"Start queue",label:"Start",service:"start_queue"}]:[]}function mt(i,e){if(e)return e.label;switch(i.runState){case"idle":return i.pendingItems===1?"Ready to start 1 room.":i.pendingItems>1?`Ready to start ${i.pendingItems} rooms.`:"Queue is empty.";case"running":return"Queue is running.";case"completed":return"Queue completed.";case"canceled":return"Queue canceled.";case"blocked":return"Route blocked. Review room access before restarting.";case"out_of_sync":return"Queue out of sync. Review robot state before restarting.";case"manual_control":return"Manual control active.";default:return`Queue state: ${ye(i.runState)}.`}}function ft(i){return ct.map(e=>({field:e.field,label:e.label,valueLabel:st(e.field,i,{})}))}function gt(i,e){const t=e.vacuumEntityId;if(!i||!t)return[];const r=i.states[t]?.attributes;return at(_t(r)?r.rooms:void 0)}function T(i,e){return e?i.states[e]?.state:void 0}function de(i){return String(i??"").trim()}function _t(i){return typeof i=="object"&&i!==null&&!Array.isArray(i)}const D=class D extends R{constructor(){super(...arguments),this._config={}}setConfig(e){if(!e||typeof e!="object")throw new Error("Invalid HA Dreame queue card configuration");this._config={...e}}getCardSize(){return 3}render(){const e=ut(this.hass,this._config),t=e.snapshot;return p`
      <ha-card>
        <div class="header">
          <div>
            <h2 class="title">${e.title}</h2>
            <p class="subtitle">${e.summary??e.entityId??"Queue controls"}</p>
          </div>
          ${t?p`<span class="state-pill ${t.runState}"
                >${this._stateLabel(t.runState)}</span
              >`:c}
        </div>

        ${e.message?p`<div class="message">${e.message}</div>`:p`
              <div class="counts">
                ${this._count("Pending",t?.pendingItems??0)}
                ${this._count("Running",t?.runningItems??0)}
                ${this._count("Done",t?.completedItems??0)}
                ${this._count("Total",t?.totalItems??0)}
              </div>
              ${e.activeControls.length||e.canClearPending?p`
                    <div class="queue-actions">
                      ${e.activeControls.map(r=>p`
                          <button
                            aria-label=${r.ariaLabel}
                            class="row-action"
                            type="button"
                            ?disabled=${!t?.configEntryId}
                            @click=${()=>this._callQueueService(t?.configEntryId,r.service)}
                          >
                            ${r.label}
                          </button>
                        `)}
                      ${e.canClearPending?p`
                            <button
                              aria-label="Clear pending queue"
                              class="row-action"
                              type="button"
                              ?disabled=${!t?.configEntryId}
                              @click=${()=>this._clearPending(t?.configEntryId)}
                            >
                              Clear pending
                            </button>
                          `:c}
                    </div>
                  `:c}
              <div class="queue-list">
                ${e.rows.length?e.rows.map(r=>p`
                        <div class="queue-row">
                          <span class="room-name">${r.roomName}</span>
                          <div class="row-actions">
                            <span class="row-status">${r.statusLabel}</span>
                            ${r.overrideControls.map(n=>p`
                                <button
                                  aria-label=${`Cycle ${r.roomName} ${this._overrideAriaField(n.field)}`}
                                  class="row-action"
                                  type="button"
                                  ?disabled=${!t?.configEntryId}
                                  @click=${()=>this._updateOverrides(t?.configEntryId,r.itemId,n.field,r.overrides)}
                                >
                                  ${n.label} ${n.valueLabel}
                                </button>
                              `)}
                            ${r.canMoveUp?p`
                                  <button
                                    aria-label=${`Move ${r.roomName} up`}
                                    class="row-action"
                                    type="button"
                                    ?disabled=${!t?.configEntryId}
                                    @click=${()=>this._moveItem(t?.configEntryId,r.itemId,r.queuePosition-1)}
                                  >
                                    Up
                                  </button>
                                `:c}
                            ${r.canMoveDown?p`
                                  <button
                                    aria-label=${`Move ${r.roomName} down`}
                                    class="row-action"
                                    type="button"
                                    ?disabled=${!t?.configEntryId}
                                    @click=${()=>this._moveItem(t?.configEntryId,r.itemId,r.queuePosition+1)}
                                  >
                                    Down
                                  </button>
                                `:c}
                            ${r.canRemove?p`
                                  <button
                                    aria-label=${`Remove ${r.roomName}`}
                                    class="row-action"
                                    type="button"
                                    ?disabled=${!t?.configEntryId}
                                    @click=${()=>this._removeItem(t?.configEntryId,r.itemId)}
                                  >
                                    Remove
                                  </button>
                                `:c}
                          </div>
                        </div>
                      `):p`<div class="message">Queue is empty.</div>`}
              </div>
              ${e.rooms.length?p`
                    <div class="section-title">Available rooms</div>
                    <div class="room-catalog">
                      ${e.rooms.map(r=>p`
                          <button
                            class="room-chip"
                            type="button"
                            ?disabled=${!t?.configEntryId}
                            @click=${()=>this._addRoom(t?.configEntryId,r.roomId,r.roomName)}
                          >
                            ${r.roomName}
                          </button>
                        `)}
                    </div>
                  `:c}
            `}
      </ha-card>
    `}_count(e,t){return p`
      <div class="count">
        <span class="count-value">${t}</span>
        <span class="count-label">${e}</span>
      </div>
    `}_stateLabel(e){return e.split("_").filter(t=>t.length>0).map(t=>t.charAt(0).toUpperCase()+t.slice(1)).join(" ")}_addRoom(e,t,r){!e||!this.hass?.callService||this.hass.callService("ha_dreame","add_queue_room",{config_entry_id:e,room_id:t,room_name:r})}_removeItem(e,t){!e||!this.hass?.callService||this.hass.callService("ha_dreame","remove_queue_item",{config_entry_id:e,item_id:t})}_moveItem(e,t,r){!e||!this.hass?.callService||this.hass.callService("ha_dreame","move_queue_item",{config_entry_id:e,item_id:t,new_position:r})}_clearPending(e){!e||!this.hass?.callService||this.hass.callService("ha_dreame","clear_pending_queue",{config_entry_id:e})}_callQueueService(e,t){!e||!this.hass?.callService||this.hass.callService("ha_dreame",t,{config_entry_id:e})}_updateOverrides(e,t,r,n){!e||!this.hass?.callService||this.hass.callService("ha_dreame","update_queue_item_overrides",{config_entry_id:e,item_id:t,overrides:ot(r,n,{})})}_overrideAriaField(e){return e==="water_volume"?"water volume":e==="suction_level"?"suction level":"repeats"}};D.properties={hass:{attribute:!1},_config:{state:!0}},D.styles=Ee`
    :host {
      display: block;
    }

    ha-card {
      display: block;
      padding: 14px;
    }

    .header {
      display: grid;
      grid-template-columns: minmax(0, 1fr) auto;
      align-items: start;
      gap: 10px;
      margin-bottom: 12px;
    }

    .title {
      margin: 0;
      font-size: 1rem;
      font-weight: 600;
      line-height: 1.25;
      overflow-wrap: anywhere;
    }

    .subtitle {
      margin: 3px 0 0;
      color: var(--secondary-text-color);
      font-size: 0.78rem;
      line-height: 1.25;
      overflow-wrap: anywhere;
    }

    .state-pill {
      border: 1px solid var(--divider-color);
      border-radius: 999px;
      color: var(--secondary-text-color);
      font-size: 0.78rem;
      line-height: 1.2;
      padding: 4px 9px;
      white-space: nowrap;
    }

    .state-pill.running {
      border-color: var(--state-active-color, #2e7d32);
      color: var(--state-active-color, #2e7d32);
    }

    .state-pill.blocked,
    .state-pill.out_of_sync,
    .state-pill.error {
      border-color: var(--error-color, #d32f2f);
      color: var(--error-color, #d32f2f);
    }

    .message {
      border: 1px solid var(--divider-color);
      border-radius: 8px;
      color: var(--secondary-text-color);
      font-size: 0.86rem;
      line-height: 1.35;
      padding: 10px;
    }

    .counts {
      display: grid;
      grid-template-columns: repeat(4, minmax(0, 1fr));
      gap: 6px;
      margin-bottom: 8px;
    }

    .count {
      border: 1px solid var(--divider-color);
      border-radius: 8px;
      min-width: 0;
      padding: 7px 8px;
    }

    .count-value {
      display: block;
      font-size: 1rem;
      font-weight: 600;
      line-height: 1.1;
    }

    .count-label {
      color: var(--secondary-text-color);
      display: block;
      font-size: 0.72rem;
      line-height: 1.2;
      margin-top: 3px;
      overflow-wrap: anywhere;
    }

    .queue-list {
      display: grid;
      gap: 6px;
    }

    .queue-actions {
      display: flex;
      justify-content: flex-end;
      margin: 0 0 12px;
    }

    .section-title {
      color: var(--secondary-text-color);
      font-size: 0.74rem;
      font-weight: 600;
      line-height: 1.2;
      margin: 12px 0 6px;
      text-transform: uppercase;
    }

    .room-catalog {
      display: flex;
      flex-wrap: wrap;
      gap: 6px;
    }

    .room-chip {
      background: transparent;
      border: 1px solid var(--divider-color);
      border-radius: 999px;
      color: var(--primary-text-color);
      cursor: pointer;
      font-family: inherit;
      font-size: 0.78rem;
      line-height: 1.2;
      max-width: 100%;
      overflow: hidden;
      padding: 5px 9px;
      text-overflow: ellipsis;
      white-space: nowrap;
    }

    .room-chip:disabled {
      color: var(--disabled-text-color, var(--secondary-text-color));
      cursor: default;
    }

    .queue-row {
      border: 1px solid var(--divider-color);
      border-radius: 8px;
      display: grid;
      gap: 8px;
      grid-template-columns: minmax(0, 1fr) auto;
      align-items: center;
      min-height: 34px;
      padding: 7px 9px;
    }

    .room-name {
      font-size: 0.88rem;
      font-weight: 600;
      line-height: 1.25;
      min-width: 0;
      overflow: hidden;
      text-overflow: ellipsis;
      white-space: nowrap;
    }

    .row-status {
      color: var(--secondary-text-color);
      font-size: 0.78rem;
      line-height: 1.25;
      white-space: nowrap;
    }

    .row-actions {
      align-items: center;
      display: flex;
      flex-wrap: wrap;
      gap: 4px;
      justify-content: flex-end;
    }

    .row-action {
      background: transparent;
      border: 1px solid var(--divider-color);
      border-radius: 999px;
      color: var(--primary-text-color);
      cursor: pointer;
      font-family: inherit;
      font-size: 0.74rem;
      line-height: 1.2;
      padding: 3px 8px;
      white-space: nowrap;
    }

    .row-action:disabled {
      color: var(--disabled-text-color, var(--secondary-text-color));
      cursor: default;
    }
  `;let G=D;customElements.get(q)||customElements.define(q,G);window.customCards=window.customCards??[];window.customCards.some(i=>i.type===q)||window.customCards.push({type:q,name:"HA Dreame Queue",description:"Queue controls for HA Dreame."});
