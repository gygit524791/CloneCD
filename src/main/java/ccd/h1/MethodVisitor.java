package ccd.h1;

import antlr.Java8BaseVisitor;
import antlr.Java8Lexer;
import antlr.Java8Parser;
import ccd.PropsLoader;
import org.antlr.v4.runtime.ParserRuleContext;
import org.antlr.v4.runtime.tree.ParseTree;
import org.antlr.v4.runtime.tree.RuleNode;
import org.antlr.v4.runtime.tree.TerminalNode;
import redis.clients.jedis.Jedis;

import java.util.Stack;

public class MethodVisitor extends Java8BaseVisitor<Integer> {
    private static int methodLimitedLine = Integer.valueOf(PropsLoader.getProperty("ccd.methodLimitedLine"));
    private final String ccdSeparate = "ccdMethodSeparate";
    private int startLine;
    private String pathFilename;
    private Jedis redis;

    @Override
    public Integer visitConstructorDeclaration(Java8Parser.ConstructorDeclarationContext ctx) {
        startLine = ctx.start.getLine();
        return visitChildren(ctx);
    }

    @Override
    public Integer visitMethodHeader(Java8Parser.MethodHeaderContext ctx) {
        startLine = ctx.start.getLine();
        return visitChildren(ctx);
    }

    @Override
    public Integer visitConstructorBody(Java8Parser.ConstructorBodyContext ctx) {
        int stopLine = ctx.stop.getLine();
        if((stopLine - startLine + 1) < methodLimitedLine)
            return null;
        visitAST(ctx, stopLine);
        return visitChildren(ctx);
    }

    @Override
    public Integer visitMethodBody(Java8Parser.MethodBodyContext ctx) {
        int stopLine = ctx.stop.getLine();
        if((stopLine - startLine + 1) < methodLimitedLine)
            return null;
        visitAST(ctx, stopLine);
        return visitChildren(ctx);
    }

    private void visitAST(ParserRuleContext ctx, int stopLine){
        String key = pathFilename + "(" + startLine + "-" + stopLine + ")";
        Stack<ParseTree> stack = new Stack<>();
        stack.push(ctx);
        int ruleIndex;
        StringBuilder statement = new StringBuilder();
        StringBuilder line = new StringBuilder();
        int beforeLine = -1;
        while(!stack.empty()){
            ParseTree node = stack.pop();
            if(node instanceof RuleNode){
                int nodeIndex = ((RuleNode) node).getRuleContext().getRuleIndex();
                if (RuleFilterForLine.ruleFilter().containsKey(nodeIndex)) {
                    ParserRuleContext ct = (ParserRuleContext)node;
                    int currentLine = ct.getStart().getLine();
                    if(beforeLine == -1){
                        beforeLine = currentLine;
                    }
                    if(currentLine != beforeLine){
                        line.deleteCharAt(line.length()-1);
                        line.append(";").append(nodeIndex+",");
                        beforeLine = currentLine;
                    }else {
                        line.append(nodeIndex+",");
                    }
                }
                ruleIndex = ((RuleNode) node).getRuleContext().getRuleIndex();
                if (RuleFilterForLine.ruleFilter().containsKey(ruleIndex)) {
                    statement.append(ruleIndex + ",");
                }
                for(int len = node.getChildCount(), i = len - 1; i >= 0; i --){
                    stack.push(node.getChild(i));
                }
            }
        }
        if(statement.length()>=1){//method statements
            statement.deleteCharAt(statement.length()-1);
        }
        if(line.length()>=1){//method line
            line.deleteCharAt(line.length()-1);
        }
        String value = line.toString() +ccdSeparate+ statement.toString();
        redis.set(key, value);
    }



    public void setPathFilename(String pathFilename) {
        this.pathFilename = pathFilename;
    }
    public void setRedis(Jedis redis) {
        this.redis = redis;
    }
}
